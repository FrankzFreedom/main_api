from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *
from src.models.assets import assets

now =  time.strftime('%Y-%m-%d %H:%M:%S')
now2 =  time.strftime('%Y%m%d%H%M%S')
db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
    responses={404: {"description": "Not found"}},
)

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con

@router.post('/addassets')
async def addassets(data:assets,current_user: User = Depends(get_current_user)):
    con = db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor(pymysql.cursors.DictCursor) as cur: 
            sqlreadbrand = "SELECT id_ass_brand,type_model_id,startsn from assets_models " #getbrand_id
            sqlreadbrand = sqlreadbrand + " JOIN assets_type ON type_model_id = id_type_ass where id_model_ass = %s"
            try:
                con.commit()
                cur.execute(sqlreadbrand,(data.id_model))
            except pymysql.Error as e: #if error print error
                return {
                    'code':500-1,
                    'detail':f'Error{e}'
                }
            if cur.rowcount  < 1 : #if not error but no model
                return {
                    'code':400,
                    'detail':"no model in data"
                }
            else:
                datamodel = cur.fetchone() 
                sqlreadser="select id_assets from assets where serial_number = %s" #check existed
                try:
                    con.commit()
                    cur.execute(sqlreadser,(data.serial))
                except pymysql.Error as e: #if error print error
                    return {
                        'code':500-2,
                        'detail':f'Error{e}'
                    }
                if cur.rowcount > 0 : #if not error but have data in db
                    return {
                        'code':300,
                        'detail':'existed'
                    }
                else:
                    if datamodel['type_model_id'] == 1 or datamodel['type_model_id'] == 2 or datamodel['type_model_id'] == 3:
                        hw_id=f"{datamodel['startsn']}{now2}{data.serial[:5]}"
                        sqladdassets = "insert into assets (stampin,hardware_id,ass_id_type,brand_id,model_id,serial_number,branch_id,remark)"
                        sqladdassets = sqladdassets + " values (%s,%s,%s,%s,%s,%s,%s,%s)"
                        try:
                            cur.execute(sqladdassets,(now,hw_id,datamodel['type_model_id'],datamodel['id_ass_brand'],data.id_model,data.serial,data.id_branch,data.remark))
                            con.commit()
                        except pymysql.Error as e: #if error print error
                            return {
                                'code':500-3,
                                'detail':f'Error{e}'
                            }   
                        sqlrecheck ="select id_assets from assets where hardware_id = %s"
                        try:
                            con.commit()
                            cur.execute(sqlrecheck,(hw_id))
                        except pymysql.Error as e: #if error print error
                            return {
                                'code':500-4,
                                'detail':f'Error{e}'
                            } 
                        if cur.rowcount > 0:
                            dataidassets = cur.fetchone()
                            sqladdmacaddress="insert into mac_address  (id_ass_macaddress,macaddress) values (%s,%s)"
                            try:
                                cur.execute(sqladdmacaddress,(dataidassets['id_assets'],data.macaddress))
                                con.commit()
                            except pymysql.Error as e: #if error print error
                                return {
                                    'code':500-5,
                                    'detail':f'Error{e}'
                                } 
                            sqlremac="select id_macaddress from mac_address where id_ass_macaddress = %s"
                            try:
                                con.commit()
                                cur.execute(sqlremac,(dataidassets['id_assets']))
                            except pymysql.Error as e: #if error print error
                                return {
                                    'code':500-6,
                                    'detail':f'Error{e}'
                                }
                            if cur.rowcount > 0:
                                return {
                                    'code':200,
                                    'detail':"success"
                                }
                            else:
                                return {
                                    'code':500,
                                    'detail':"Failed insert mac_address"
                                }
                        else:
                            return {
                                    'code':500,
                                    'detail':"Failed insert assets"
                                }
                    else:
                        hw_id=f"{datamodel['startsn']}{now2}{data.serial[:5]}"
                        sqladdassets = "insert into assets (stampin,hardware_id,ass_id_type,brand_id,model_id,serial_number,branch_id,remark)"
                        sqladdassets = sqladdassets + " values (%s,%s,%s,%s,%s,%s,%s,%s)"
                        try:
                            cur.execute(sqladdassets,(now,hw_id,datamodel['type_model_id'],datamodel['id_ass_brand'],data.id_model,data.serial,data.id_branch,data.remark))
                            con.commit()
                        except pymysql.Error as e: #if error print error
                            return {
                                'code':500-3,
                                'detail':f'Error{e}'
                            }   
                        sqlrecheck ="select id_assets from assets where hardware_id = %s"
                        try:
                            con.commit()
                            cur.execute(sqlrecheck,(hw_id))
                        except pymysql.Error as e: #if error print error
                            return {
                                'code':500-4,
                                'detail':f'Error{e}'
                            } 
                        if cur.rowcount > 0:
                            return {
                                'code':200,
                                'detail':"success"
                            }
                        else:
                            return {
                                'code':500,
                                'detail':"Error insert assets"
                            }

@router.get('/getallassets')
async def getallassets(current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
        sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
        sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
        sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
        
        try:
            con.commit()
            cur.execute(sqlget)
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            datareturn =cur.fetchall()
            return {
                'code':200,
                'detail':datareturn
            }
        else :
            return {
                'code':400,
                'detail':"no data"
            }

@router.get('/getallassetsspecifically')
async def getspecificallymacaddress(current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch,id_macaddress,macaddress from assets" 
        sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
        sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
        sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
        sqlget= sqlget + " JOIN mac_address ON id_assets = id_ass_macaddress"
        
        try:
            con.commit()
            cur.execute(sqlget)
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            datareturn =cur.fetchall()
            return {
                'code':200,
                'detail':datareturn
            }
        else :
            return {
                'code':400,
                'detail':"no data"
            }

@router.get('/getassetsfromtype/{type_id}')
async def getassetsfromtype(type_id:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlchecktype = 'select id_type_ass from assets_type where id_type_ass = %s'
        try: 
            con.commit()
            cur.execute(sqlchecktype,type_id)
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        
        if cur.rowcount > 0 :
            if int(type_id) == 1 or int(type_id) == 2 or int(type_id) == 3:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch,id_macaddress,macaddress from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " JOIN mac_address ON id_assets = id_ass_macaddress"
                sqlget= sqlget + " where ass_id_type = %s"
                
                try:
                    con.commit()
                    cur.execute(sqlget,type_id)
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data"
                    }
            else:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " where ass_id_type = %s"
                
                
                try:
                    con.commit()
                    cur.execute(sqlget,(type_id))
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data assets"
                    }
        else:
            return {
                'code':400,
                'detail':"no data type"
            }

@router.get('/getassetsfromserial/{serial_number}')
async def getassetsfromserial(serial_number:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlgettype="select ass_id_type from assets where serial_number = %s"
        try:
            con.commit()
            cur.execute(sqlgettype,(serial_number))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            datatype = cur.fetchone()
            if datatype['ass_id_type'] == 1 or  datatype['ass_id_type'] == 2 or datatype['ass_id_type'] == 3:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch,id_macaddress,macaddress from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " JOIN mac_address ON id_assets = id_ass_macaddress"
                sqlget= sqlget + " where serial_number = %s"
                
                try:
                    con.commit()
                    cur.execute(sqlget,(serial_number))
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data"
                    }
            else:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " where serial_number = %s"
                try:
                    con.commit()
                    cur.execute(sqlget,serial_number)
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data"
                    }

@router.get('/getassetsfromhradwareid/{hradware_id}')
async def getassetsfromhradwareid(hradware_id:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlgettype="select ass_id_type from assets where hardware_id = %s"
        try:
            con.commit()
            cur.execute(sqlgettype,(hradware_id))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            datatype = cur.fetchone()
            if datatype['ass_id_type'] == 1 or  datatype['ass_id_type'] == 2 or datatype['ass_id_type'] == 3:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch,id_macaddress,macaddress from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " JOIN mac_address ON id_assets = id_ass_macaddress"
                sqlget= sqlget + " where hardware_id = %s"
                
                try:
                    con.commit()
                    cur.execute(sqlget,(hradware_id))
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data"
                    }
            else:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " where hardware_id = %s"
                try:
                    con.commit()
                    cur.execute(sqlget,(hradware_id))
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data"
                    }
        else:
            return {
                'code':400,
                'detail':'no serial in data'
            }


@router.get('/getassetsmacaddress/{macaddress}')
async def getassetsmacaddress(macaddress:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlgetmac="select id_ass_macaddress from mac_address where macaddress = %s"
        try:
            con.commit()
            cur.execute(sqlgetmac,(macaddress))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            datamac = cur.fetchone()
            sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch,id_macaddress,macaddress from assets" 
            sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
            sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
            sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
            sqlget= sqlget + " JOIN mac_address ON id_assets = id_ass_macaddress"
            sqlget= sqlget + " where id_assets = %s"
            
            try:
                con.commit()
                cur.execute(sqlget,(datamac['id_ass_macaddress']))
            except pymysql.Error () as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                datareturn =cur.fetchall()
                return {
                    'code':200,
                    'detail':datareturn
                }
            else :
                return {
                    'code':400,
                    'detail':"no data"
                }
        else:
            return {
                'code':400,
                'detail':'no macaddress in data'
            }

@router.get('/getassetsfrommodels/{model_id}')
async def getassetsfrommodels(model_id:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlgettypemodel = "select type_model_id from assets_models where id_model_ass = %s"
        try:
            con.commit()
            cur.execute(sqlgettypemodel,(model_id))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount >  0 :
            datatype=cur.fetchone()
            if datatype['type_model_id'] == 1 or datatype['type_model_id'] == 2 or datatype['type_model_id'] == 3:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch,id_macaddress,macaddress from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " JOIN mac_address ON id_assets = id_ass_macaddress"
                sqlget= sqlget + " where model_id = %s"
                
                try:
                    con.commit()
                    cur.execute(sqlget,(model_id))
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data"
                    }
            else:
                sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
                sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
                sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
                sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
                sqlget= sqlget + " where model_id = %s"
                try:
                    con.commit()
                    cur.execute(sqlget,(model_id))
                except pymysql.Error () as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    datareturn =cur.fetchall()
                    return {
                        'code':200,
                        'detail':datareturn
                    }
                else :
                    return {
                        'code':400,
                        'detail':"no data"
                    }
        else:
            return {
                'code':400,
                'detail':'no model in data'
            }

@router.get('/getassetsfrombrand/{brand_id}')
async def getassetsfrombrand(brand_id:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlcheckbrand="select id_brand from assets_brand where id_brand = %s"
        try:
            con.commit()
            cur.execute(sqlcheckbrand,(brand_id))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
            sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
            sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
            sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
            sqlget= sqlget + " where brand_id = %s"
            try:
                con.commit()
                cur.execute(sqlget,(brand_id))
            except pymysql.Error () as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                datareturn =cur.fetchall()
                return {
                    'code':200,
                    'detail':datareturn
                }
            else :
                return {
                    'code':400,
                    'detail':"no data"
                }
        else:
            return {
                'code':400,
                'detail':'no brand in data'
            }

@router.get('/getassetsfromagency/{agency_id}')
async def getassetsfromagency(agency_id:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlcheckagnecy="select id_agency from agency where id_agency = %s"
        try:
            con.commit()
            cur.execute(sqlcheckagnecy,(agency_id))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
            sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
            sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
            sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
            sqlget= sqlget + " where agency_ass_id = %s"
            try:
                con.commit()
                cur.execute(sqlget,(agency_id))
            except pymysql.Error () as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                datareturn =cur.fetchall()
                return {
                    'code':200,
                    'detail':datareturn
                }
            else :
                return {
                    'code':400,
                    'detail':"no data"
                }

        else:
            return {
                'code':400,
                'detail':"no agency in data"
            }

@router.get('/getssetsfromcurrent/{current_name}')
async def getssetsfromcurrent(current_name:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
        sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
        sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
        sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
        sqlget= sqlget + " where current = %s"
        
        try:
            con.commit()
            cur.execute(sqlget,(current_name))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            datareturn =cur.fetchall()
            return {
                'code':200,
                'detail':datareturn
            }
        else :
            return {
                'code':400,
                'detail':"no data"
            }


@router.get('/getassetsfrombranch/{branch_id}')
async def getassetsfrombranch(branch_id:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlcheckagnecy="select id_branch from branch where id_branch = %s"
        try:
            con.commit()
            cur.execute(sqlcheckagnecy,(branch_id))
        except pymysql.Error () as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            sqlget="SELECT id_assets,hardware_id,CURRENT,brand_id,model_id,serial_number,branch_id,remark,model_name,brand_name,id_type_ass,name_type_ass,id_status,status_name,id_agency,name_agency,name_branch from assets" 
            sqlget= sqlget + " JOIN assets_models ON model_id = id_model_ass JOIN assets_brand ON brand_id = id_brand"
            sqlget= sqlget + " JOIN assets_type ON ass_id_type = id_type_ass JOIN status_ass ON status_ass_id = id_status"
            sqlget= sqlget + " JOIN branch ON branch_id = id_branch JOIN agency ON agency_ass_id = id_agency"
            sqlget= sqlget + " where agency_ass_id = %s"
            try:
                con.commit()
                cur.execute(sqlget,(branch_id))
            except pymysql.Error () as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                datareturn =cur.fetchall()
                return {
                    'code':200,
                    'detail':datareturn
                }
            else :
                return {
                    'code':400,
                    'detail':"no data"
                }

        else:
            return {
                'code':400,
                'detail':"no branch in data"
            }

@router.put('/editassets/{id_assets}/{model_id}/{remark}/{serial}')
async def editassets(id_assets:str,model_id:str,remark:str,serial:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            sqlcheckassets="select id_assets,model_id,ass_id_type from assets where id_assets = %s"
            try:
                con.commit()
                cur.execute(sqlcheckassets,(id_assets))
            except pymysql.Error as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            
            if cur.rowcount > 0 :
                dataoldassets=cur.fetchone()
                if dataoldassets['model_id'] == int(model_id):
                    sqlupdate="update assets set remark = %s,serial_number = %s where id_assets = %s"
                    try:
                        cur.execute(sqlupdate,(remark,serial,id_assets))
                        con.commit()
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    return {
                        'code':200,
                        'detail':'success'
                    }
                else:
                    sqlgetdatamodel="select id_ass_brand,model_name,type_model_id from assets_models where id_model_ass = %s"
                    try:
                        con.commit()
                        cur.execute(sqlgetdatamodel,(model_id))
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    if cur.rowcount > 0 :
                        datamodel=cur.fetchone()
                        if dataoldassets['ass_id_type'] ==  datamodel['type_model_id']:
                            sqlupdate="update assets set remark = %s,serial_number = %s, model_id = %s ,brand_id = %s where id_assets = %s"
                            try:
                                cur.execute(sqlupdate,(remark,serial,model_id,datamodel['id_ass_brand'],id_assets))
                                con.commit()
                            except pymysql.Error as e:
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                }   
                            return {
                                'code':200,
                                'detail':'success'
                            }
                        else:
                            sqlgetsn="select startsn from assets_type where id_type_ass = %s"
                            try:
                                con.commit()
                                cur.execute(sqlgetsn,(datamodel['type_model_id']))
                            except pymysql.Error as e:
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                } 
                            startsn= cur.fetchone()
                            newhw = f"{startsn['startsn']}{now2}{serial[:5]}"
                            sqlupdate="update assets set remark = %s,serial_number = %s, model_id = %s ,brand_id = %s,hardware_id = %s,ass_id_type = %s where id_assets = %s"
                            try:
                                cur.execute(sqlupdate,(remark,serial,model_id,datamodel['id_ass_brand'],newhw,datamodel['type_model_id'],id_assets))
                            except pymysql.Error as e:
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                } 
                            con.commit()  
                            return {
                                'code':200,
                                'detail':'success'
                            }
                    else:
                        return {
                            'code':400,
                            'detail': 'no model in data'
                        }


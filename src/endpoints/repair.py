from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *
now =  time.strftime('%Y-%m-%d %H:%M:%S')

router = APIRouter(
    prefix="/repair",
    tags=["repair"],
    responses={404: {"description": "Not found"}},
)

db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con


@router.post('/sendrepair/{id_assets}/{problems}/{who_or_wheres}')
async def sendrepair(id_assets:str,problems:str,who_or_wheres:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    with con.cursor() as cur:
        sqlcheckass="select id_assets from assets where id_assets = %s"
        try:
            con.commit()
            cur.execute(sqlcheckass,(id_assets))
        except pymysql.Error as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount < 1 :
            return {
                'code':400,
                'detail':"no data in assets "
            }
        else:
            sqlcheckstatus="select id_repair from repair WHERE  repair_id_ass = %s AND stampsuccess IS  NULL"
            try:
                con.commit()
                cur.execute(sqlcheckstatus,(id_assets))
            except pymysql.Error as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                return {
                    'code':300,
                    'detail':'assets is repair now or claim'
                }
            else:
                sqladd="insert into repair (repair_id_ass,problems,who_where,stamsend) values (%s,%s,%s,%s)"
                try:
                    cur.execute(sqladd,(id_assets,problems,who_or_wheres,now))
                    con.commit()
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                sqlreck="select id_repair from repair WHERE  repair_id_ass = %s AND stampsuccess IS  NULL"
                try:
                    con.commit()
                    cur.execute(sqlreck,(id_assets))
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    sqlupdatestatus="update assets set status_ass_id = 3 where id_assets = %s"
                    try:
                        cur.execute(sqlupdatestatus,(id_assets))
                        con.commit()
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    sqlckstatus="select id_assets from assets where id_assets = %s and status_ass_id = 3"
                    try:
                        con.commit()
                        cur.execute(sqlckstatus,(id_assets))
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    if cur.rowcount > 0:
                        return {
                            'code':200,
                            'detail':'success'
                        }
                    else:
                        return {
                        'code':500,
                        'detail':'Error update status'
                    }
                else:
                    return {
                        'code':500,
                        'detail':'Error insert repair'
                    }

@router.post('/sendclaim/{id_assets}/{problems}/{who_or_wheres}')
async def sendclaim(id_assets:str,problems:str,who_or_wheres:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    with con.cursor() as cur:
        sqlcheckass="select id_assets from assets where id_assets = %s"
        try:
            con.commit()
            cur.execute(sqlcheckass,(id_assets))
        except pymysql.Error as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount < 1 :
            return {
                'code':400,
                'detail':"no data in assets "
            }
        else:
            sqlcheckstatus="select id_repair from repair WHERE  repair_id_ass = %s AND stampsuccess IS  NULL"
            try:
                con.commit()
                cur.execute(sqlcheckstatus,(id_assets))
            except pymysql.Error as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                return {
                    'code':300,
                    'detail':'assets is repair now or claim'
                }
            else:
                sqladd="insert into repair (repair_id_ass,problems,who_where,stamsend) values (%s,%s,%s,%s)"
                try:
                    cur.execute(sqladd,(id_assets,problems,who_or_wheres,now))
                    con.commit()
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                sqlreck="select id_repair from repair WHERE  repair_id_ass = %s AND stampsuccess IS  NULL"
                try:
                    con.commit()
                    cur.execute(sqlreck,(id_assets))
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    sqlupdatestatus="update assets set status_ass_id = 4 where id_assets = %s"
                    try:
                        cur.execute(sqlupdatestatus,(id_assets))
                        con.commit()
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    sqlckstatus="select id_assets from assets where id_assets = %s and status_ass_id = 4"
                    try:
                        con.commit()
                        cur.execute(sqlckstatus,(id_assets))
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    if cur.rowcount > 0:
                        return {
                            'code':200,
                            'detail':'success'
                        }
                    else:
                        return {
                        'code':500,
                        'detail':'Error update status'
                    }
                else:
                    return {
                        'code':500,
                        'detail':'Error insert repair'
                    }

@router.get("/getall")
async def getallrepairorclaim(current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlgetreclaim="SELECT id_repair,id_assets,problems,who_where,stamsend,stampsuccess,hardware_id,id_agency,name_agency,id_branch,name_branch,id_status,status_name FROM repair"
        sqlgetreclaim= sqlgetreclaim +" JOIN assets ON repair_id_ass = id_assets JOIN agency ON agency_ass_id = id_agency"
        sqlgetreclaim= sqlgetreclaim + " JOIN branch ON branch_id = id_branch JOIN status_ass ON status_ass_id = id_status"
        try:
            con.commit()
            cur.execute(sqlgetreclaim)
        except pymysql.Error as e :
            return {
                'code':500,
                'detail':F"Error:{e}"
            }
        if cur.rowcount > 0 :
            datareply = cur.fetchall()
            return {
                'code':200,
                'detail': datareply
            }
        else:
            return {
                'code':400,
                'detail':"no data repair and claim"
            }

@router.get("/getnosuccess")
async def getnosuccess(current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlgetreclaim="SELECT id_repair,id_assets,problems,who_where,stamsend,stampsuccess,hardware_id,id_agency,name_agency,id_branch,name_branch,id_status,status_name FROM repair"
        sqlgetreclaim= sqlgetreclaim +" JOIN assets ON repair_id_ass = id_assets JOIN agency ON agency_ass_id = id_agency"
        sqlgetreclaim= sqlgetreclaim + " JOIN branch ON branch_id = id_branch JOIN status_ass ON status_ass_id = id_status"
        sqlgetreclaim= sqlgetreclaim + " where stampsuccess IS NULL"
        try:
            con.commit()
            cur.execute(sqlgetreclaim)
        except pymysql.Error as e :
            return {
                'code':500,
                'detail':F"Error:{e}"
            }
        if cur.rowcount > 0 :
            datareply = cur.fetchall()
            return {
                'code':200,
                'detail': datareply
            }
        else:
            return {
                'code':400,
                'detail':"no data repair and claim no success"
            }

@router.get("/getsuccess")
async def getsuccess(current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlgetreclaim="SELECT id_repair,id_assets,problems,who_where,stamsend,stampsuccess,hardware_id,id_agency,name_agency,id_branch,name_branch,id_status,status_name FROM repair"
        sqlgetreclaim= sqlgetreclaim +" JOIN assets ON repair_id_ass = id_assets JOIN agency ON agency_ass_id = id_agency"
        sqlgetreclaim= sqlgetreclaim + " JOIN branch ON branch_id = id_branch JOIN status_ass ON status_ass_id = id_status"
        sqlgetreclaim= sqlgetreclaim + " where stampsuccess IS NOT NULL"
        try:
            cur.execute(sqlgetreclaim)
        except pymysql.Error as e :
            return {
                'code':500,
                'detail':F"Error:{e}"
            }
        if cur.rowcount > 0 :
            datareply = cur.fetchall()
            return {
                'code':200,
                'detail': datareply
            }
        else:
            return {
                'code':400,
                'detail':"no data repair and claim success"
            }

@router.put("/confirmsuccess/{id_repair}")
async def confirmsuccess(id_repair:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur:
            sqlchecksuccess="select id_repair,repair_id_ass from repair where id_repair = %s and  stampsuccess IS NULL"
            try:
                con.commit()
                cur.execute(sqlchecksuccess,(id_repair))
            except pymysql.Error as e:
                return {
                    'code':500,
                    'detail':f'Error:{e}'
                }
            if cur.rowcount > 0:
                dataassets_id = cur.fetchone()
                print(dataassets_id[1])
                sqlconfirm="update repair set stampsuccess = %s where id_repair = %s"
                try:
                    cur.execute(sqlconfirm,(now,id_repair))
                    con.commit()
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f'Error:{e}'
                    }
                sqlrecheck ="select id_repair from repair where id_repair = %s and  stampsuccess IS NULL"
                try:
                    cur.execute(sqlrecheck,(id_repair))
                    
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f'Error:{e}'
                    }
                if cur.rowcount >  0 :
                    return {
                        'code':500,
                        'detail':'Error confirm'
                    }
                else:
                    sqlupdatestatus="update assets set status_ass_id = 1 where id_assets = %s"
                    try:
                        cur.execute(sqlupdatestatus,(dataassets_id[1]))
                        con.commit()
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f'Error:{e}'
                        }
                    sqlcheckupst="select id_assets from assets where id_assets = %s and status_ass_id = 1"
                    try:
                        cur.execute(sqlcheckupst,(dataassets_id[1]))
                        
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f'Error:{e}'
                        }
                    if cur.rowcount > 0 :
                        return {
                            'code':200,
                            'detail':'success'
                        }
                    else:
                        return {
                            'code':500,
                            'detail':"Error update status"
                        }
            else:
                return {
                    'code':400,
                    'detail':" already confirmed or no data."
                }

@router.put("/edit/{id_repair}/{problem}/{whowhere}")
async def editrepair(id_repair:str,problem:str,whowhere:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    if current_user.rule != "31":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor () as cur:
            sqlcheckid = "select stampsuccess from repair where id_repair = %s"
            try:
                con.commit()
                cur.execute(sqlcheckid,(id_repair))
            except pymysql.Error as e:
                return {
                    'code':500,
                    'detail':f'Error:{e}'
                }
            if cur.rowcount > 0 :
                datastamp = cur.fetchone()
                if datastamp[0] is not 'NULL' :
                    return {
                    'code':301,
                    'detail':"This list has been completed."
                }
                else: 

                    sqlupdate = "update repair set problems = %s , who_where = %s where id_repair = %s"
                    try:
                        cur.execute(sqlupdate,(problem,whowhere,id_repair))
                        con.commit()
                    except pymysql.Error as e:
                                return {
                                    'code':500,
                                    'detail':f'Error:{e}'
                                }
                    return {
                        'code':200,
                        'detail':'success'
                    }
            
            else:
                return {
                    'code':400,
                    'detail':"no data id_repair"
                }
from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *
now =  time.strftime('%Y-%m-%d %H:%M:%S')

router = APIRouter(
    prefix="/etc",
    tags=["etc"],
    responses={404: {"description": "Not found"}},
)

db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con

@router.post("/addbrand/{brand_name}") #เพิ้่มแบรนด์อุปกรณ์
async def addbrand(brand_name:str,current_user: User = Depends(get_current_user)): 
    con = db_connect() #สั่งให้เช็คสถานะDATABASE 
    with con.cursor() as cur : #เช็คBrand_name ว่ามีอยู่แล้วหรือไหม
        sqlcheck_name=f"select id_brand,brand_name from assets_brand where brand_name = '{brand_name}' "
        con.commit()
        cur.execute(sqlcheck_name)
        if cur.rowcount > 0: #ถ้ามี
            databrand= cur.fetchall()
            brand_detail = { #ข้อมูลที่เจอ และจะนำส่งให้API
                "id": databrand[0][0],
                "name":databrand[0][1]
            }
            return {
                "code": 300,
                "detail": brand_detail
            }
        else : #ถ้ายังไม่มีในข้อมูล
            with con.cursor() as cur_insert :
                
                try:
                    sql_insert=f"insert into assets_brand (brand_name) values ('{brand_name}')" #เพิ่มข้อมูลในdatabase
                    cur_insert.execute(sql_insert)
                    con.commit() 
                    sqlcheck_name2=f"select id_brand,brand_name from assets_brand where brand_name = '{brand_name}' " #ดุึงข้อมูลที่พึ่งเพิ่มไป
                    con.commit()
                    cur_insert.execute(sqlcheck_name2)
                    if cur_insert.rowcount > 0 :
                        sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (13,'เพิ่มแบรนด์อุปกรณ์',%s)" #เพิ่มข้อูล
                        try:
                            cur.execute(sqllog,(current_user.username_id))
                        except pymysql.Error as e : #ถ้าผิดพลาด
                            return {
                            'code':500,
                            'details':f"Error:{e}"
                          }
                        con.commit()
                        databrand= cur_insert.fetchall()
                        brand_detail = { #ข้อมูลที่เจอ และจะนำส่งให้API
                            "id": databrand[0][0],
                            "name":databrand[0][1]
                        }
                        return {
                            "code": 200,
                            "detail": brand_detail
                            
                        }
                    else :
                        return {      #กรณีที่SQL ไม่สามารถติดต่อได้ 
                            "code":500,
                            "detail":"SQL ERROR "
                        }
                except:
                    return 
                    {
                            "code":500,
                            "detail":"SQL ERROR "
                        }


@router.post("/addmodel/{brand_id}/{model_name}")
async def addmodel(brand_id:str,model_name:str,type_id:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur:
            sqlcheckbrand="select id_brand from assets_brand where id_brand = %s"
            try:
                con.commit()
                cur.execute(sqlcheckbrand,(brand_id))
            except pymysql.Error as e:
                return {
                    'code':500-1,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount < 1:
                return {
                    'code':400,
                    'detail':'no brand_id'
                }
            else:
                sqlcheckmodelname="select id_model_ass from assets_models where model_name = %s"
                try:
                    con.commit()
                    cur.execute(sqlcheckmodelname,(model_name))
                except pymysql.Error as e:
                    return {
                        'code':500-2,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    return {
                        'code':300,
                        'detail':'existed'
                    }
                else:
                    sqladdmodel="insert into assets_models (id_ass_brand,model_name,type_model_id) values (%s,%s,%s)"
                    try:
                        cur.execute(sqladdmodel,(brand_id,model_name,type_id))
                    except pymysql.Error as e:
                        return {
                            'code':500-3,
                            'detail':f"Error:{e}"
                        }
                    con.commit()
                    sqlcheckagain="select id_model_ass from assets_models where model_name = %s "
                    try:
                        con.commit()
                        cur.execute(sqlcheckagain,(model_name))
                    except pymysql.Error as e:
                        return {
                            'code':500-4,
                            'detail':f"Error:{e}"
                        }
                    if cur.rowcount > 0 :
                        sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (14,'เพิ่มโมเดล',%s)" #เพิ่มข้อมูล
                        try:
                            cur.execute(sqllog,(current_user.username_id))
                        except pymysql.Error as e : #ถ้าผิดพลาด
                            return {
                            'code':500,
                            'details':f"Error:{e}"
                          }
                        con.commit()
                        return {
                            'code':200,
                            'detail':'success'
                        }
                    else :
                        return {
                            'code':500-5,
                            'detail':'error insert assets_models'
                        }

@router.post("/addstatus/{status_name}") #add "Brand" in Database
async def addstatus(status_name:str,current_user: User = Depends(get_current_user)):

    con = db_connect() #สั่งให้เช็คสถานะDATABASE 
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur : #เช็ค status_name ว่ามีอยู่แล้วหรือไหม
            sqlcheck_name=f"select id_status,status_name from status_ass where status_name = '{status_name}' "
            con.commit()
            cur.execute(sqlcheck_name)
            
            if cur.rowcount > 0: #ถ้ามี
                datastatus = cur.fetchall()
                status_detail = { #ข้อมูลที่เจอ และจะนำส่งให้API
                    "id": datastatus[0][0],
                    "name":datastatus[0][1]
                }
                return {    #กรณีที่มีเหมือนกัน  
                    "code": 300,
                    "detail": status_detail
                }
            else : #ถ้ายังไม่มีในข้อมูล
                with con.cursor() as cur_insert :
                    
                    try:
                        sql_insert=f"insert into status_ass (status_name) values ('{status_name}')" #เพิ่มข้อมูลในdatabase
                        cur_insert.execute(sql_insert)
                        con.commit() 
                    except:    
                        return  #กรณีที่SQL ไม่สามารถติดต่อได้ 
                        {
                                "code":500,
                                "detail":"SQL ERROR "
                            }
                    else:
                        sqlcheck_name2=f"select id_status,status_name from status_ass where status_name = '{status_name}' " #ดุึงข้อมูลที่พึ่งเพิ่มไป
                        con.commit()
                        cur_insert.execute(sqlcheck_name2)
                        if cur_insert.rowcount > 0 :
                            sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (15,'เพิ่มสถานะ',%s)" #เพิ่มข้อมูล
                            try:
                              cur.execute(sqllog,(current_user.username_id))
                            except pymysql.Error as e : #ถ้าผิดพลาด
                                return {
                               'code':500,
                              'details':f"Error:{e}"
                                  }
                            con.commit()
                            datastatus= cur_insert.fetchall()
                            status_detail = { #ข้อมูลที่เจอ และจะนำส่งให้API
                                "id": datastatus[0][0],
                                "name":datastatus[0][1]
                            }
                            return {
                                "code": 200,
                                "detail": status_detail
                                
                            }
                        else :
                            return {
                                "code":400,
                                "detail":"No Data in Status"
                            }

@router.get("/getbrand") #ค้นหารายการยี่ห้อ
async def getbrand(current_user: User = Depends(get_current_user)):
    con = db_connect()

    try:
        with con.cursor() as cur :
            sqlget="select id_brand,brand_name from assets_brand "
            con.commit()
            cur.execute(sqlget)
            if cur.rowcount > 0 : #ถ้ามีข้อมูลอยู่
                databrand = cur.fetchall()
                detail_brand =[] #เก็บค่าข้อมูล
                for items_brand in databrand:
                    dt={
                    "id":items_brand[0],
                    "name":items_brand[1]
                    }
                    detail_brand.append(dt)
                return {
                    "code":200,
                    "detail": detail_brand
                }
            else: #ถ้าไม่มีข้อมูล
                return {
                    "code":400,
                    "detail": "NO DATA"
                }
    except    pymysql.Error as x :
        return {
                    "code":500,
                    'detail': f"Error:{x}"
                    
                }

@router.get("/gettype") #ค้นหารายการประเภท
async def gettype(current_user: User = Depends(get_current_user)):
    con = db_connect()
    try:
        with con.cursor() as cur :
            sqlget="select id_type_ass,name_type_ass from assets_type "
            con.commit()
            cur.execute(sqlget)
            if cur.rowcount > 0 :
                datatype = cur.fetchall()
                detail_type = []
                for item_type in datatype :
                    dt={
                        "id":item_type[0],
                        "name":item_type[1]
                    }
                    detail_type.append(dt)
                return{
                    "code": 200,
                    "detail":detail_type
                }
            else: 
                return{
                    "code": 400,
                    "detial" : "No Information"
                }
    except    pymysql.Error as x :
        return{
                "code":500,
            'detail': f"Error:{x}"
        }

@router.get("/getstatus") #ค้นหาารายการสถานะ
async def getstatus (current_user: User = Depends(get_current_user)):
    con = db_connect()
    try:
        with con.cursor() as cur :
            sqlget="select id_status,status_name from status_ass "
            con.commit()
            cur.execute(sqlget)
            if cur.rowcount > 0 :
                datastatus = cur.fetchall()
                detailstatus = []
                for status in datastatus:
                    dt={
                        "id":status[0],
                        "name":status[1]
                    }
                    detailstatus.append(dt)
                return{
                    "code": 200,
                    "detail":detailstatus
                }
            else: 
                    return{
                        "code": 400,
                        "detial" : "No Information"
                    }
    except    pymysql.Error as x :
             return{
                 "code":500,
              'detail': f"Error:{x}"
            }

@router.get("/getmodels") #ค้นหารายการรุ่น
async def getmodels(current_user: User = Depends(get_current_user)):
     con = db_connect()
     try:
        with con.cursor() as cur :
            sqlget = "SELECT id_model_ass,model_name,brand_name,id_brand,type_model_id,name_type_ass FROM assets_models JOIN assets_brand ON id_ass_brand  = id_brand JOIN assets_type ON type_model_id = id_type_ass "
            con.commit()
            cur.execute(sqlget)
            if cur.rowcount > 0 :
                datamodels = cur.fetchall()
                detail_models = []
                for item_models in datamodels:
                    dt={
                        "id_model":item_models[0],
                        "name_model":item_models[1],
                        "id_brand":item_models[2],
                        "name_brand":item_models[3],
                        "type_id":item_models[4],
                        'type_name':item_models[5]


                    }
                    detail_models.append(dt)
                return {
                    "code": 200,
                    "detail" : detail_models 
                }
            else :
                return {
                    "code" :400,
                    "detail" : "No Information"
                }
     except    pymysql.Error as x :
                return{
                  "code":500,
                  'detail': f"Error:{x}"
                }

@router.put("/editbrand/{brand_name}/{id_brand}") #แก้ไขชื่อแบรนด์
async def editbrand (brand_name:str,id_brand:str,current_user: User = Depends(get_current_user)):
    con =db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur:
            sqlckname = "select id_brand from assets_brand where brand_name = %s" #เช็คว่ามีชื่อซ้ำหรือไหม
            try:
                con.commit()
                cur.execute(sqlckname,(brand_name))

            except pymysql.Error as e: #ถ้าติดปัญหา
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            else: #ถ้าไม่ติดปัญหา
                if cur.rowcount > 0 : #ถ้ามี
                    return {
                        'code':300,
                        'detail':'existed'
                    }
                else:
                    sqlck1 = "select id_brand from assets_brand where id_brand = %s" #หาของเก่าจากไอดี
                    
                    try:
                        con.commit()
                        cur.execute(sqlck1,(id_brand))
                        
                    except pymysql.Error as e: #ถ้าติดปัญหา
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    else: #ถ้าไม่ติดปัญหา
                        if cur.rowcount > 0 : #ถ้าเจอจากการค้นหาไอดี
                            dataitbrand = cur.fetchall() #เอาค่าที่selectมาใส่
                            sqlupdate = "update assets_brand set brand_name = %s  where id_brand = %s "
                            try: #ถ้าติดปัญหา
                                cur.execute(sqlupdate,(brand_name,id_brand))
                                con.commit()
                            except pymysql.Error as e:
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                }
                            else: #ถ้าไม่ติดปัญหา
                                sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (16,'แก้ไขชื่อแบรนด์',%s)" #เพเิ่มข้อมูล
                                try:
                                    cur.execute(sqllog,(current_user.username_id))
                                except pymysql.Error as e : #ถ้าผิดพลาด
                                 return {
                                        'code':500,
                                        'details':f"Error:{e}"
                                  }
                                con.commit()
                                brand_detail = {
                                    'id':dataitbrand[0][0],
                                    'name':brand_name
                                }
                                    
                                return {
                                    'code':200,
                                    'detail':brand_detail
                                }
                        else: #ถ้าไม่เจอจากการค้นหาไอดี
                            return {
                                'code':400,
                                'detail':"NO DATA"
                            }

@router.put("/edittypes/{name_type}/{id_type}") #แก้ไขชื่อประเภท
async def edittypes (name_type:str,id_type:str,current_user: User = Depends(get_current_user)):
    con =db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur: 
            sqlcheckname = "select id_type_ass from assets_type where name_type_ass = %s" #เช็คว่ามีชื่อซ้ำหรือไหม
            try:
                con.commit()
                cur.execute(sqlcheckname,(name_type))
                
            except pymysql.Error as e: #ถ้ามีปัญหา
                
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            else: #ถ้าไม่มีปัญหา
                if cur.rowcount > 0 : #ถ้าเจอชื่อซ้ำ
                    
                    return {
                        
                        'code':300,
                        'detail':"existed"

                    }

                else: #ถ้าไม่เจอซ้ำ
                    sqlcheckid = "select id_type_ass from assets_type where id_type_ass = %s " #ค้นหาไอดีจากไอดีที่ส่งมา
                    try:
                        con.commit()
                        cur.execute(sqlcheckid,(id_type))
                        
                    except pymysql.Error as e: #ถ้ามีปัญหา
                        
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    else: #ถ้าไม่มีปัญหา
                        if cur.rowcount > 0 : #ถ้าเจอข้อมูล
                            dataid = cur.fetchall() #ข้อมูลไอดี
                            sqlupdatename = "update assets_type set name_type_ass = %s where  id_type_ass = %s "
                            try:
                                cur.execute(sqlupdatename,(name_type,id_type))
                                con.commit()
                                
                            except pymysql.Error as e: #ถ้ามีปัญหา
                                
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                }
                            else: #ถ้าไม่มีปัญหา 
                                sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (17,'แก้ไขชื่อประเภท',%s)" #เพิ่มข้อมูล
                                try:
                                     cur.execute(sqllog,(current_user.username_id))
                                except pymysql.Error as e : #ถ้าผิดพลาด
                                    return {
                                        'code':500,
                                        'details':f"Error:{e}"
                                  }
                                con.commit()
                                detail_change = { #jsondata
                                    'id':dataid[0][0],
                                    'name': name_type
                                }
                                return {
                                    'code':200,
                                    'detail': detail_change
                                }
                        else:  #ถ้าไม่เจอข้อมูล 
                            
                            return {
                                    'code':400,
                                    'detail': "NO DATA"
                                }

@router.put("/editmodels/{model_name}/{id_model}") #แก้ไขชือรุ่น
async def editmodels(model_name:str,id_model:str,current_user: User = Depends(get_current_user)): 
    con = db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur:
            sqlcheckname = "select id_model_ass from assets_models where model_name = %s" #เช็คว่ามีชื่อซ้ำหรือไหม
            try:
                con.commit()
                cur.execute(sqlcheckname,(model_name))
            except pymysql.Error as e: #ถ้ามีปัญหา
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            else:  #ถ้าไม่มีปัญหา
                if cur.rowcount > 0 : #ถ้าเจอซ้ำ
                    return {
                        'code':300,
                        'detail':"existed"
                    }
                else: #ถ้าไม่ซ้ำ
                    sqlupname = "update assets_models set model_name = %s where  id_model_ass = %s " #แก้ไขชื่อ
                    try:
                        cur.execute(sqlupname,(model_name,id_model))
                        con.commit()
                    except pymysql.Error as e : #ถ้ามีปัญหา
                        return {
                                'code':500,
                                'detail':f"Error:{e}"
                            }
                    else: #ถ้าไม่มีปัญหา
                        sqlreck="select id_model_ass from assets_models where id_model_ass = %s " #หาอีกรอบ
                        try:
                            con.commit()
                            cur.execute(sqlreck,(id_model))
                        except pymysql.Error as e : #ถ้ามีปัญหา
                            return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                }
                        else: #ถ้าไม่มีปัญหา
                            sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (18,'แก้ไขชื่อรุ่น',%s)" #เพิ่มข้อมูล
                            try:
                                     cur.execute(sqllog,(current_user.username_id))
                            except pymysql.Error as e : #ถ้าผิดพลาด
                                    return {
                                        'code':500,
                                        'details':f"Error:{e}"
                                  }
                            con.commit()
                            if cur.rowcount > 0 : #ถ้าหาเจอ
                                return {
                                    'code':200,
                                    'detail':{
                                        'id':id_model,
                                        'name':model_name
                                    }
                                }
                            else:  #ถ้าหาไม่เจอ
                                return {
                                    'code':400,
                                    'detail':"NO DATA"
                                }
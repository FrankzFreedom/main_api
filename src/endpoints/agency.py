from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *
now =  time.strftime('%Y-%m-%d %H:%M:%S')

router = APIRouter(
    prefix="/agency",
    tags=["agency"],
    responses={404: {"description": "Not found"}},
)

db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con


@router.post("/addagency/{nameagnecy}")
async def addagency(nameagnecy:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur:
            sqlcheckname ="select id_agency from agency where name_agency = %s" #check existed nameagency
            try:
                con.commit()
                cur.execute(sqlcheckname,(nameagnecy))
            except pymysql.Error as e : # if error return error
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            else:
                if cur.rowcount > 0 :
                    return {
                        'code':300,
                        'detail':"existed"
                    }   
                else:
                    sqladd="insert into agency (name_agency) values (%s)" #sqladdagency
                    try:
                        cur.execute(sqladd,(nameagnecy))
                        con.commit()
                    except pymysql.Error as e : # if error return error
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        } 
                    else:
                        sqlrecheck="select id_agency from agency where name_agency = %s" #recheck id after add success
                        try:
                            con.commit()
                            cur.execute(sqlrecheck,(nameagnecy))
                        except pymysql.Error as e : # if error return error
                            return {
                                'code':500,
                                'detail':f"Error:{e}"
                            }   
                        else:
                            if cur.rowcount > 0 : #addsuccess
                                dataid_agency = cur.fetchall()
                                data_return = {
                                    'id':dataid_agency[0][0],
                                    'name':nameagnecy
                                }
                                sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (8,'เพิ่มหน่วยงาน',%s)" #เพิ่มข้อมูล
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
                                    'detail':data_return

                                }
                            else: #addfailed
                                return {
                                    'code':500,
                                    'detail':"failed"
                                }

@router.get("/getagency")
async def getagency(current_user: User = Depends(get_current_user)):
    con = db_connect()
    with con.cursor() as cur:
        sqlget="select id_agency,name_agency from agency" #getdat all in agency table
        try:
            con.commit()
            cur.execute(sqlget)
        except pymysql.Error as e: #if error return error
            return {
                'code':500,
                'detail':F"Error:{e}"
            }
        else: #if not error
            if cur.rowcount > 0 : #if have data in table
                dataagency = cur.fetchall()
                data_return =[]
                for item in dataagency:
                    dataagency_return ={
                        'id':item[0],
                        'name':item[1]
                    }
                    data_return.append(dataagency_return)
                return {
                    'code':200,
                    'detail':data_return
                }
            else:  #no data in table
                return{
                    'code':400,
                    'detail':'no data'
                }

@router.put("/editagency/{idagency}/{nameagency}")
async def editagency(idagency:str,nameagency:str,current_user: User = Depends(get_current_user)):
    
    con = db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur:
            sqlckid ="select id_agency from agency where id_agency = %s" #check id in table
            try:
                con.commit()
                cur.execute(sqlckid,(idagency))
                
            except pymysql.Error as e: #if error return error
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            else : #if not error
                if cur.rowcount > 0 : #if id in table
                    sqlexname = "select id_agency from agency where name_agency = %s" #check existed name in table
                    try:
                        con.commit()
                        cur.execute(sqlexname,(nameagency))
                    except pymysql.Error as e: #if error return error
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    else: #if not error
                        if cur.rowcount > 0 : #if name in tabel
                            return {
                                'code':300,
                                'detail':"existed"
                            }
                        else: #no name in table
                            sqlupdatename="update agency set name_agency = %s where id_agency = %s"
                            try:
                                cur.execute(sqlupdatename,(nameagency,idagency))
                                con.commit()
                            except pymysql.Error as e: #if error return error
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                }
                            else: #if not error
                                sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (10,'แก้ไขหนวยงาน',%s)" #เพิ่มข้อมูล
                                try: 
                                    cur.execute(sqllog,(current_user.username_id))
                                except pymysql.Error as e :  #ถ้าผิดพลาด
                                    return {
                                        'code':500,
                                        'details':f"Error:{e}"
                                    }
                                con.commit()
                                newdata = {
                                    'id':idagency,
                                    'name':nameagency
                                }
                                return {
                                    'code':200,
                                    'detail':newdata
                                }
                else:  #no id in table
                    return {
                        'code':400,
                        'detail':"no id in data"
                    }

@router.delete("/removeagency/{idagency}")
async def removeagency(idagency:str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    if current_user.rule != "31":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur:
            sqlckid = "select id_agency from agency where id_agency = %s"
            try:
                con.commit()
                cur.execute(sqlckid,(idagency))
            except pymysql.Error as e: #if error return error
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            else: #not error
                if cur.rowcount > 0 : # have id in table
                    sqlremove="delete from agency where id_agency = %s" #remove for id
                    try:
                        cur.execute(sqlremove,(idagency))
                        con.commit()
                    except pymysql.Error as e: #if error return error
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    else: #not error
                        sqlreck = "select id_agency from agency where id_agency = %s" #recheck id in table
                        try: 
                            con.commit()
                            cur.execute(sqlreck,(idagency))
                        except pymysql.Error as e: #if error return error
                            return {
                                'code':500,
                                'detail':f"Error:{e}"
                            }
                        else: #not error
                            if cur.rowcount  < 1: #nodata  = success
                                sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (9,'ลบหน่วยงาน',%s)"
                                try:
                                    cur.execute(sqllog,(current_user.username_id))
                        
                                except pymysql.Error as e :
                                    return {
                                        'code':500,
                                        'details':f"Error:{e}"
                                    }
                                con.commit()
                                return {
                                    'code':200,
                                    'detail':"success"
                                }
                            else: #have data = error
                                return {
                                    'code':500,
                                    'detail':"Failed"
                                }
                else: #no id in table
                    return {
                        'code':400,
                        'detail':"no data"
                    }
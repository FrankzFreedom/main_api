from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *
from src.models.lic import *

now =  time.strftime('%Y-%m-%d %H:%M:%S')
now2 =  time.strftime('%Y%m%d%H%M%S')
db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

router = APIRouter(
    prefix="/manage",
    tags=["manage"],
    responses={404: {"description": "Not found"}},
)

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con

@router.get("/get_mn_all")
async def get_mn_all (current_user: User = Depends(get_current_user)):
    con = db_connect()
    try : 
        with con.cursor() as cur:
            sql_mn = "SELECT id_manage,manage_id_ass,old_owner,agency_id_manage,branch_id_manage,stampstart,stampend,hardware_id from manage JOIN assets " #ดึงข้อมูล
            cur.execute(sql_mn)
            con.commit()
            if cur.rowcount > 0 : #ถ้ามี
                datalicense = cur.fetchall()
                datadetaillices = []
                for row  in datalicense: #นำข้อมูลที่ได้มาจัดเก็บในรูปแบบของ list ชื่อ datadetaillices
                    dt={
                        "id_manage": row  [0],
                        "manage_id_ass": row [1],
                        "old_owner":row [2],
                        "agency_id_manage":row[3],
                        "branch_id_manage":row [4],
                        "stampstart":row [5],
                        "stampend":row [6],
                        "hardware_id":row [7]
                    }
                    datadetaillices.append(dt)

                return {
                    "code":200,
                    "detail":datadetaillices
                }
            else:   #ถ้ามีไม่มีข้อมูล
                return { 
                    "code":400,
                    "detail" : "No matching records found" 
                }
    except pymysql.Error as e : #ถ้าเกิดข้อผิดพลาด
        return {
           "code" :500,
           "detail": str(e)
        }

    finally:
        con.close() #ออกdatabase

@router.get("/get_mn_id")
async def get_mn_id (get_mn_id: str,current_user: User = Depends(get_current_user)):
    con = db_connect()
    try : 
        with con.cursor() as cur:
            sql_mn = "SELECT id_manage,manage_id_ass,old_owner,agency_id_manage,branch_id_manage,stampstart,stampend,hardware_id from manage JOIN assets WHERE manage_id_ass = %s " #ดึงข้อมูล 
            cur.execute(sql_mn,(get_mn_id))
            con.commit()
            if cur.rowcount > 0 : #ถ้ามี
                datalicense = cur.fetchall()
                datadetaillices = []
                for row  in datalicense: #นำข้อมูลที่ได้มาจัดเก็บในรูปแบบของ list ชื่อ datadetaillices
                    dt={
                        "id_manage": row  [0],
                        "manage_id_ass": row [1],
                        "old_owner":row [2],
                        "agency_id_manage":row[3],
                        "branch_id_manage":row [4],
                        "stampstart":row [5],
                        "stampend":row [6],
                        "hardware_id":row [7]
                    }
                    datadetaillices.append(dt)

                return {
                    "code":200,
                    "detail":datadetaillices
                }
            else:   #ถ้ามีไม่มีข้อมูล
                return { 
                    "code":400,
                    "detail" : "No matching records found" 
                }
    except pymysql.Error as e : #ถ้าเกิดข้อผิดพลาด
        return {
           "code" :500,
           "detail": str(e)
        }

    finally:
        con.close() #ออกdatabase
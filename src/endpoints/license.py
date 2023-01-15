from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *
from src.models.lic import *

now =  time.strftime('%Y-%m-%d %H:%M:%S')
now2 =  time.strftime('%Y%m%d%H%M%S')
db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

router = APIRouter(
    prefix="/license",
    tags=["license"],
    responses={404: {"description": "Not found"}},
)

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con



def insert_lic(id_lic,lic_key):                     #Function ที่ใช่ในการ Insert ข้อมูล
    con = db_connect()                              #เช็คสถานะ Datatbase Connect
    with con.cursor() as cur_insert: 
        sql_insert2 = f"INSERT INTO license_keys (lic_id_dt ,lic_keys) VALUES (%s,%s)"    #เพิ่มข้อมูลใน license_keys อ้างอิงจาก lic_id_key
        cur_insert.execute(sql_insert2,(id_lic,lic_key))
        con.commit()   

        sql_insert2 = f"SELECT COUNT(lic_id_dt) FROM license_keys WHERE lic_id_dt = %s"    #เพิ่มข้อมูลใน license_keys อ้างอิงจาก lic_id_key
        cur_insert.execute(sql_insert2,(id_lic))
        con.commit()   
        countlist = cur_insert.fetchall()
        count = countlist[0][0]

        sql_select = f"UPDATE license_details SET volume = %s WHERE id_lic_dt = %s "            #Update 'volume' ลงใน license_details 
        cur_insert.execute(sql_select,(count,id_lic))
        con.commit()  

def insert_lic2(lic_dt_name,lic_dt_type,expire,lic_key):
    con = db_connect()                              #เช็คสถานะ Datatbase Connect
    with con.cursor() as cur_insert: 
        sql_select = f"SELECT id_lic_dt ,lic_dt_name ,lic_dt_type ,expire ,volume FROM license_details WHERE lic_dt_name = %s AND lic_dt_type = %s AND expire = %s " #เพิ่มข้อมูลในdatabase
        cur_insert.execute(sql_select,(lic_dt_name ,lic_dt_type ,expire))               #ทำการ Add ไปที่ฐานข้อมูล
        con.commit()                                                                    #ทำการส่งข้อมูลไปที่ฐานข้อมูลเพื่อส่งค่ากลับมาเป็น ID ของ License
        get_id = cur_insert.fetchall()              
        lic_id = get_id[0][0]                                                           #รับค่า ID จาก get_id ตำแหน่ง [0][0]    

        sql_insert2 = f"INSERT INTO license_keys (lic_id_dt ,lic_keys) VALUES ('{lic_id}','{lic_key}')"    #เพิ่มข้อมูลใน license_keys อ้างอิงจาก lic_id_key
        cur_insert.execute(sql_insert2)             
        con.commit()   

        sql_insert2 = f"SELECT COUNT(lic_id_dt) FROM license_keys WHERE lic_id_dt = %s"                     #นับจำนวน Key เพื่อเพิ่มใน Volume
        cur_insert.execute(sql_insert2,(lic_id))
        con.commit()   
        countlist = cur_insert.fetchall()
        count = countlist[0][0]

        sql_select = f"UPDATE license_details SET volume = %s WHERE id_lic_dt = %s "                        #Update 'volume' ลงใน license_details 
        cur_insert.execute(sql_select,(count,lic_id))
        con.commit()                                    #ทำการ Update 'volume' ไปที่ license_details

def insert_new_lic(lic_dt_name ,lic_dt_type ,expire):                           #Function ที่ใช่ในการ Insert ข้อมูล
    con = db_connect()                                  #เช็คสถานะ Datatbase Connect
    with con.cursor() as cur_insert: 
        sql_insert2 = f"INSERT INTO license_details (lic_dt_name ,lic_dt_type ,expire,volume) VALUES (%s,%s,%s,'0')"    #เพิ่มข้อมูลใน license_keys อ้างอิงจาก lic_id_key
        cur_insert.execute(sql_insert2,(lic_dt_name ,lic_dt_type ,expire))
        con.commit()              


@router.post("/addketforlic")              #addlicense On Database
async def addlicense(lic_dt : keys,current_user: User = Depends(get_current_user)) : 
    con = db_connect()                              #เช็คสถานะ Datatbase Connect
    m = 0 
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur: 
            sqlcheck_name = "SELECT id_lic_dt,lic_dt_name ,lic_dt_type ,expire ,volume FROM license_details WHERE id_lic_dt = %s "
            cur.execute(sqlcheck_name,(lic_dt.id_lic))                      #ทำการ Add ไปที่ฐานข้อมูล
            con.commit()   
            try :                                           #ทำการลองใส่ข้อมูลว่าทำได้หรือไม่ ถ้าไม่ได้จะไป except
                if cur.rowcount > 0 :                       #ถ้าข้อมูลมีใน License_Details
                    for i in range(len(lic_dt.lic_keys)) :
                        sqlcheck_name = "SELECT id_lic_dt ,lic_dt_name ,lic_dt_type ,expire ,volume,lic_keys FROM license_details LEFT JOIN license_keys ON license_keys.lic_id_dt = license_details.id_lic_dt WHERE id_lic_dt = %s AND lic_keys = %s"
                        cur.execute(sqlcheck_name,(lic_dt.id_lic,lic_dt.lic_keys[i]))                           #ทำการ Add ไปที่ฐานข้อมูล
                        con.commit()                            #ทำการส่งข้อมูลไปที่ฐานข้อมูลเพื่อเช็ค
                        if cur.rowcount > 0 :
                            m = m + 1
                        else :
                            insert_lic(lic_dt.id_lic ,lic_dt.lic_keys[i])       #ส่งค่าไปยัง Function insert_lic

                    if len(lic_dt.lic_keys) == m:               #ถ้าข้อมูลมีอยู่แล้ว
                        lic_detail = {                          #ข้อมูลตามลำดับ Array
                                "ID" : lic_dt.id_lic,
                                "Key" : lic_dt.lic_keys
                            }
                        return {                                
                            "code" : 300 ,                      #ถ้ามีข้อมูลซ้ำ
                            "detail" : lic_detail
                        }
                    else :                                      #ถ้าข้อมูลไม่มีอยู่แต่แรก
                        lic_detail = {                          #ข้อมูลตามลำดับ Array
                                    "ID" : lic_dt.id_lic,
                                    "Key" : lic_dt.lic_keys,
                                }
                        return { 
                            "code" : 200 ,                      #ส่งข้อมูลสำเร็จ
                            "detail" : lic_detail
                        }
                else :                                          #ถ้าข้อมูลไม่มีใน License_Details
                    return { 
                        "code" : 400 ,                          #ถ้าไม่มีข้อมูล
                        "detail" : "No Data"
                    }
            except :                                            #ถ้ามีข้อผิดพลาด
                return { 
                        "code" : 500 ,                          
                        "detail" : "SQL Error"
                    }

@router.post("/addlicense")              #addlicenseOn Database
async def addlicense(lic_dt : keysadd,current_user: User = Depends(get_current_user)) :
    con = db_connect()                              #เช็คสถานะ Datatbase Connect
    m = 0 
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor() as cur: 
            try : 
                sqlcheck_name = "SELECT id_lic_dt ,lic_dt_name ,lic_dt_type ,expire ,volume FROM license_details WHERE lic_dt_name = %s AND lic_dt_type = %s AND expire = %s"
                cur.execute(sqlcheck_name,(lic_dt.lic_dt_name ,lic_dt.lic_dt_type ,lic_dt.expire ))                  #ทำการ Add ไปที่ฐานข้อมูล
                con.commit()                                    #ทำการส่งข้อมูลไปที่ฐานข้อมูลเพื่อเช็ค

                if cur.rowcount > 0 :
                    for i in range(len(lic_dt.lic_keys)) :
                        sqlcheck_name = "SELECT id_lic_dt ,lic_dt_name ,lic_dt_type ,expire ,volume,lic_keys FROM license_details LEFT JOIN license_keys ON license_keys.lic_id_dt = license_details.id_lic_dt WHERE lic_dt_name = %s AND lic_dt_type = %s AND expire = %s AND lic_keys = %s"
                        cur.execute(sqlcheck_name,(lic_dt.lic_dt_name ,lic_dt.lic_dt_type ,lic_dt.expire ,lic_dt.lic_keys[i]))                  #ทำการ Add ไปที่ฐานข้อมูล
                        con.commit()                                #ทำการส่งข้อมูลไปที่ฐานข้อมูลเพื่อเช็ค
                        if cur.rowcount > 0 :
                            m = m + 1
                        else :
                            insert_lic2(lic_dt.lic_dt_name ,lic_dt.lic_dt_type ,lic_dt.expire ,lic_dt.lic_keys[i])

                    if len(lic_dt.lic_keys) == m:
                        lic_detail = {                          #โชว์ข้อมูลของ License
                                "name" : lic_dt.lic_dt_name,
                                "type" : lic_dt.lic_dt_type,
                                "Expire" : lic_dt.expire,
                                "Key" : lic_dt.lic_keys,
                                "Sum Lic" : len(lic_dt.lic_keys) - (len(lic_dt.lic_keys) - m),  # มี Key ใน License ซ้ำกี่ตัว
                                "New Insert" : len(lic_dt.lic_keys) - m                         # มี Key เพิ่มเข้าไปใหม่ใน License กี่ตัว
                            }
                        return { 
                            "code" : 300 ,                      #ถ้ามีข้อมูลซ้ำ
                            "detail" : lic_detail               #โชว์ข้อมูลจาก lic_detail
                        }

                    else :
                        lic_detail = {                          #โชว์ข้อมูลของ License
                                    "name" : lic_dt.lic_dt_name,
                                    "type" : lic_dt.lic_dt_type,
                                    "Expire" : lic_dt.expire,
                                    "Key" : lic_dt.lic_keys,
                                    "Sum Lic" : len(lic_dt.lic_keys) - (len(lic_dt.lic_keys) - m),  # มี Key ใน License ซ้ำกี่ตัว
                                    "New Insert " : len(lic_dt.lic_keys) - m                        # มี Key เพิ่มเข้าไปใหม่ใน License กี่ตัว
                                }
                        return { 
                            "code" : 200 ,                      #รับส่งข้อมูลสำเร็จ
                            "detail" : lic_detail               #โชว์ข้อมูลจาก lic_detail
                        }
                    
                else : 
                    insert_new_lic(lic_dt.lic_dt_name ,lic_dt.lic_dt_type ,lic_dt.expire )          #เพิ่ม License ใหม่ที่ยังไม่มีอยู่ไปที่ License_Detail โดย Function "insert_new_lic"

                    for i in range(len(lic_dt.lic_keys)) :                                          #วนค่าเพิ่มข้อมูล Key ใน License ใหม่
                        insert_lic2(lic_dt.lic_dt_name ,lic_dt.lic_dt_type ,lic_dt.expire ,lic_dt.lic_keys[i])

                    lic_detail = {                                      # โชว์ข้อมูลของ License
                                    "name" : lic_dt.lic_dt_name,
                                    "type" : lic_dt.lic_dt_type,
                                    "Expire" : lic_dt.expire,
                                    "Key" : lic_dt.lic_keys,
                                    "Sum Lic" : len(lic_dt.lic_keys),   # มี Key ใน License ซ้ำกี่ตัว

                                }

                    return {                                    # ถ้าเพิ่มข้อมูลสำเร็จ
                        "code" : 200 ,
                        "detail" : lic_detail,                  # โชว์ข้อมูลจาก lic_detail
                        "Note" : "Successfully Insert New License"
                    }

            except :                                            #ถ้าเกิด Error
                return {                                    
                        "code" : 500 ,                      
                        "detail" : "SQL Error"
                    }

#ค้นหาlic ทั้งหมดที่มี 
@router.get("/getlicense")
async def getlicense(current_user: User = Depends(get_current_user)):
    con = db_connect() #เชื่อมต่อฐานข้อมูล
    try :
        with con.cursor() as cur: #คำสั่ง SQL เพื่อดึงข้อมูลจากฐานข้อมูล โดยจะมีการเชื่อมโยงข้อมูลระหว่างตาราง license_details และ license_type 
            sql= "select id_lic_dt ,lic_dt_name ,lic_dt_type,volume,expire , lic_type_name from license_details JOIN license_type ON license_type.id_lic_type = license_details.lic_dt_type " 
            cur.execute(sql)
            con.commit()
            if cur.rowcount > 0 : #ถ้ามี
                datalicense = cur.fetchall()
                datadetaillices = []
                for row  in datalicense: #นำข้อมูลที่ได้มาจัดเก็บในรูปแบบของ list ชื่อ datadetaillices
                    dt={
                        "id": row  [0],
                        "name": row [1],
                        "type":row [2],
                        "type_name":row[5],
                        "volume":row [3],
                        "expire":row [4]
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
    except pymysql.Error as e :
        return {
           "code" :500,
           "detail": str(e)
        }

    finally:
        con.close() #ออกdatabase
    

# ค้นหาlic จากtypelic
@router.get("/getfromtype")
async def getfromtype(type: str,current_user: User = Depends(get_current_user)): #เก็บค่าพารามิเตอร์
    con = db_connect() #เชื่อมต่อฐานข้อมูล
    try:
        with con.cursor() as cur:
            sql = "SELECT id_lic_dt, lic_dt_name, lic_dt_type, volume, expire, id_lic_type, lic_type_name, id_keys, lic_keys FROM license_details JOIN license_type "
            sql1 = sql + "ON license_type.id_lic_type = license_details.lic_dt_type JOIN license_keys ON license_keys.lic_id_dt = license_details.id_lic_dt WHERE lic_dt_type = %s"
            # คำสั่ง sql ดึงข้อมูลจากตารางโดยข้อมูลในตาราง license_details เชื่อมกับ ตาราง license_type โดยการดึงข้อมูลจะดึงได้ตามเงื่อนไขว่า lic_dt_type ว่าเป็นtypeรับมาจากค่า parameter ไหน  แล้วดึงเฉพาะ type นั้นๆ    
            cur.execute(sql1, (type,))
            con.commit()
            if cur.rowcount > 0: #ถ้ามี
                data = cur.fetchall()
                detail_type = []
                for row in data:
                    dt = {
                        "id_lic_dt": row  [0],
                        "id_dt_name": row [1],
                        "lic_dt_type":row [2],
                        "lic_type_name":row[6],
                        "exp":row [4],
                        "volume":row [3],
                        "id_key": row[7], 
                        "lic_key" : row[8]
                     
                    }
                    detail_type.append(dt)
                return {
                    "code": 200,
                    "detail": detail_type
                } 
            else:     #ถ้ามีไม่มีข้อมูล
                return {
                    "code": 400,
                    "detail": "No matching records found"
                }
    except pymysql.Error as e:
        return {
            "code": 500,
            "detail": str(e)
        }

    finally:
        con.close() #ออกdatabase


#ดึงคีย์เฉพาะที่ยังไม่ใช้งานออกมาโชว์
@router.get("/getfromidlic/{lic_id}")
async def getlicid(lic_id:str,current_user: User = Depends(get_current_user)):
    con = db_connect() #เชื่อมต่อฐานข้อมูล
    try :
        with con.cursor() as cur :
            sqlget= "SELECT id_keys,lic_keys,status_keys,lic_dt_name FROM license_keys JOIN license_details WHERE status_keys = 'Unused' and lic_id_dt = %s"  #คำสั่งsql ดึงข้อมูลจากตาราง license_keys โดยที่จะดึงได้ก็ต่อเมื่อ key นั้น Unused
            cur.execute(sqlget,(lic_id))
            con.commit()
            if cur.rowcount > 0 : #ถ้ามี 
                datalicensekeys = cur.fetchall()
                dt_lic_keys = []
                for row  in datalicensekeys:
                    dt={
                        "Status_keys": row[2],
                        "lic_dt_name" : row[3],
                        "lic_keys": row[1],
                        "id_keys": row[0]
                    }
                    dt_lic_keys.append(dt)

                return {
                    "code":200,
                    "detail":dt_lic_keys
                }
            else:  #ถ้าไม่มีข้อมูลในตาราง
                return {
                    "code":400,
                    "detail" : "No matching records found" 
                }
    except pymysql.Error as e :
        return {
           "code" :500,
           "detail":  str(e)
        }
    finally:
        con.close() #ออกdatabase
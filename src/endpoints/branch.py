from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *
now =  time.strftime('%Y-%m-%d %H:%M:%S')

router = APIRouter(
    prefix="/branch",
    tags=["branch"],
    responses={404: {"description": "Not found"}},
)

db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con


@router.post('/add/{branchname}')
async def addbranch(branchname:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            sqlcheckname="select id_branch from branch where name_branch = %s"
            try:
                con.commit()
                cur.execute(sqlcheckname,(branchname))
            except pymysql.Error as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                return {
                    'code':300,
                    'detail':'Existed'
                }    
            else:
                sqladd="insert into branch (name_branch) values (%s)"
                try:
                    cur.execute(sqladd,(branchname))
                    con.commit()
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                sqlrecheck = "select id_branch,name_branch from branch where name_branch = %s"
                try:
                    con.commit()
                    cur.execute(sqlrecheck,(branchname))
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (11,'เพิ่มสาขา',%s)" #เพิ่มข้อมูล
                    try:
                        cur.execute(sqllog,(current_user.username_id))
                    except pymysql.Error as e : #ถ้าผิดพลาด
                        return {
                            'code':500,
                            'details':f"Error:{e}"
                        }
                    con.commit()
                    dataadd=cur.fetchone()
                    return {
                        'code':200,
                        'detail':dataadd
                    }
                else:
                    return {
                        'code':500,
                        'detail':"Error insert branch"
                    }

@router.get('/getall')
async def getbrachall(current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor(pymysql.cursors.DictCursor) as cur:
        sqlget="select id_branch,name_branch from branch "
        try:
            con.commit()
            cur.execute(sqlget)
        except pymysql.Error as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            datareturn=cur.fetchall()
            return {
                'code':200,
                'detail':datareturn
            }
        else:
            return {
                'code':400,
                'detail':'no data'
            }

@router.put('/edit/{id_branch}/{namebranch}')
async def editbranch(id_branch:str,namebrach:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    if current_user.rule == "11":
        return {
            'code':321,
            'detail':" Type User Not allowed "
        }
    else:
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            sqlgetid="select id_branch from branch where id_branch = %s"
            try:
                con.commit()
                cur.execute(sqlgetid,(id_branch))
            except pymysql.Error as e:
                return {
                    'code':500,
                    'detail':f"Error:{e}"
                }
            if cur.rowcount > 0 :
                sqlcheckname = "select id_branch from branch where name_branch = %s"
                try:
                    con.commit()
                    cur.execute(sqlcheckname,(namebrach))
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    return {
                        'code':300,
                        'detail':'existed namebranch'
                    }
                else:
                    sqledit="UPDATE branch SET name_branch = %s  where id_branch = %s"
                    try:
                        cur.execute(sqledit,(namebrach,id_branch))
                        con.commit()
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    sqllog ="insert into logs_systems(log_types,log_msg,log_user_id) values (12,'แก้ไขสาขา',%s)" #เพิ่มข้อมูล 
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
                        'detail':"success"
                    }
            else:
                return {
                    'code':400,
                    'detail':'no data branch'
                }
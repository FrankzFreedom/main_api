from fastapi import FastAPI,APIRouter
import pymysql
import time
from .users import *


now =  time.strftime('%Y-%m-%d %H:%M:%S')
now2 =  time.strftime('%Y%m%d%H%M%S')
db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")

router = APIRouter(
    prefix="/doc",
    tags=["doc"],
    responses={404: {"description": "Not found"}},
)

def db_connect(): #Reconnect DATABASE
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host="34.87.30.13",user="root",password="Ops2022",database="test_assets")
    return db_con

@router.post("/sendtocurrent/{id_assets}/{current_name}/{agency_id}/{branch_id}")
async def  sendtocurrent(id_assets:str,current_name:str,agency_id:str,branch_id:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor() as cur:
        sqlcheckstatusfree="select status_ass_id from assets where  id_assets = %s  LIMIT 1"
        try:
            con.commit()
            cur.execute(sqlcheckstatusfree,(id_assets))
        except pymysql.Error as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            dataassets = cur.fetchone()
            print(dataassets[0])
            if int(dataassets[0]) == 1 :
                docs_id = f"{now2}-test"
                sqladddocs ="insert into docs (id_docs,type_docs,datework,to_user,agency_id_docs,branch_id_docs)"
                sqladddocs =sqladddocs + " values (%s,'currents',%s,%s,%s,%s)"
                try:
                    cur.execute(sqladddocs,(docs_id,now,current_name,agency_id,branch_id))
                    con.commit()
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                sqlcheckadd="select id_docs from docs where id_docs = %s"
                try:
                    con.commit()
                    cur.execute(sqlcheckadd,(docs_id))
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    sqlinsertdetail="insert into docs_details (docs_id,doc_id_ass) values (%s,%s)"
                    try:
                        cur.execute(sqlinsertdetail,(docs_id,id_assets))
                        con.commit()
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    sqlrecheckdt="select id_docs_dt from docs_details where docs_id = %s "
                    try:
                        con.commit()
                        cur.execute(sqlrecheckdt,(docs_id))
                    
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    if cur.rowcount > 0 :
                        sqlchangestatus="update assets set status_ass_id = 2 where id_assets = %s"
                        try:
                            cur.execute(sqlchangestatus,(id_assets))
                            con.commit()
                        except pymysql.Error as e:
                            return {
                                'code':500,
                                'detail':f"Error:{e}"
                            }
                        recheckstatus="select status_ass_id from assets where id_assets = %s"
                        try:
                            con.commit()
                            cur.execute(recheckstatus,(id_assets))
                            
                        except pymysql.Error as e:
                            return {
                                'code':500,
                                'detail':f"Error:{e}"
                            }
                        datanewstatus=cur.fetchone()
                        if int(datanewstatus[0]) == 2 :
                            sqlinsertmanage="insert into manage (manage_id_ass,old_owner,remark,agency_id_manage,branch_id_manage,stampstart)"
                            sqlinsertmanage= sqlinsertmanage + " values (%s,%s,'test',%s,%s,%s)"
                            try:
                                cur.execute(sqlinsertmanage,(id_assets,current_name,agency_id,branch_id,now))
                                con.commit()
                            except pymysql.Error as e:
                                return {
                                    'code':5005,
                                    'detail':f"Error:{e}"
                                }
                            sqlchecklogs="select id_manage from manage where  manage_id_ass = %s and stampend is null"
                            try:
                                con.commit()
                                cur.execute(sqlchecklogs,(id_assets))
                            
                            except pymysql.Error as e:
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                }
                            if cur.rowcount > 0 :
                                return {
                                    'code':200,
                                    'detail':"success"
                                }
                            else:
                                return {
                                    'code':500,
                                    'detail':"Error insert manage"
                                }
                        else:
                            return {
                                'code':500,
                                'detail':"Error update status"
                            }
                    else:
                        return {
                            'code':500,
                            'detail':"Error insert detail"
                        }
                else:
                    return {
                        'code':500,
                        'detail':"Error insert docs"
                    }

            else:
                return {
                    'code':300,
                    'detail':"Not Ready to use"
                }
        else:
            return {
                'code':400,
                'detail':"no assets_id"
            }
    return 0


@router.post("/givetostore/{id_assets}/{current_name}/{agency_id}/{branch_id}")
async def  givetostore(id_assets:str,current_name:str,agency_id:str,branch_id:str,current_user: User = Depends(get_current_user)):
    con=db_connect()
    with con.cursor() as cur:
        sqlcheckstatusfree="select status_ass_id from assets where  id_assets = %s  LIMIT 1"
        try:
            con.commit()
            cur.execute(sqlcheckstatusfree,(id_assets))
        except pymysql.Error as e:
            return {
                'code':500,
                'detail':f"Error:{e}"
            }
        if cur.rowcount > 0 :
            dataassets = cur.fetchone()
            if int(dataassets[0]) == 2 :
                docs_id = f"{now2}tssd-test"
                sqladddocs ="insert into docs (id_docs,type_docs,datework,to_user,agency_id_docs,branch_id_docs)"
                sqladddocs =sqladddocs + " values (%s,'backs',%s,%s,%s,%s)"
                try:
                    cur.execute(sqladddocs,(docs_id,now,current_name,agency_id,branch_id))
                    con.commit()
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                sqlcheckadd="select id_docs from docs where id_docs = %s"
                try:
                    con.commit()
                    cur.execute(sqlcheckadd,(docs_id))
                except pymysql.Error as e:
                    return {
                        'code':500,
                        'detail':f"Error:{e}"
                    }
                if cur.rowcount > 0 :
                    sqlinsertdetail="insert into docs_details (docs_id,doc_id_ass) values (%s,%s)"
                    try:
                        cur.execute(sqlinsertdetail,(docs_id,id_assets))
                        con.commit()
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    sqlrecheckdt="select id_docs_dt from docs_details where docs_id = %s "
                    try:
                        con.commit()
                        cur.execute(sqlrecheckdt,(docs_id))
                    
                    except pymysql.Error as e:
                        return {
                            'code':500,
                            'detail':f"Error:{e}"
                        }
                    if cur.rowcount > 0 :
                        sqlchangestatus="update assets set status_ass_id = 1 where id_assets = %s"
                        try:
                            cur.execute(sqlchangestatus,(id_assets))
                            con.commit()
                        except pymysql.Error as e:
                            return {
                                'code':500,
                                'detail':f"Error:{e}"
                            }
                        recheckstatus="select status_ass_id from assets where id_assets = %s"
                        try:
                            con.commit()
                            cur.execute(recheckstatus,(id_assets))
                            
                        except pymysql.Error as e:
                            return {
                                'code':500,
                                'detail':f"Error:{e}"
                            }
                        datanewstatus=cur.fetchone()
                        if int(datanewstatus[0]) == 1 :
                            sqlserach="select id_manage from manage where manage_id_ass = %s and stampend is null LIMIT 1"
                            try:
                                con.commit()
                                cur.execute(sqlserach,(id_assets))
                            
                            except pymysql.Error as e:
                                return {
                                    'code':500,
                                    'detail':f"Error:{e}"
                                }
                            if cur.rowcount > 0 :
                                id_manage = cur.fetchone()
                                sqlupdate="update manage set stampend = %s where id_manage = %s"
                                try:
                                    cur.execute(sqlupdate,(now,id_manage[0]))
                                    con.commit()
                                except pymysql.Error as e:
                                    return {
                                        'code':500,
                                        'detail':f"Error:{e}"
                                    }
                                sqlrecheckmanage="select id_manage from manage where id_manage = %s and stampend is not null LIMIT 1"
                                try:
                                    con.commit()
                                    cur.execute(sqlrecheckmanage,(id_manage[0]))
                            
                                except pymysql.Error as e:
                                    return {
                                        'code':500,
                                        'detail':f"Error:{e}"
                                    }
                                if cur.rowcount > 0 :
                                    return {
                                        'code':200,
                                        'detail':"success"
                                    }
                                else:
                                    return {
                                        'code':500,
                                        'detail':"Error update manage"
                                    }
                            else:
                                return {
                                    'code':400,
                                    'detail':'no data in manage'
                                }
                        else:
                            return {
                                'code':500,
                                'detail':"Error update status"
                            }
                    else:
                        return {
                            'code':500,
                            'detail':"Error insert detail"
                        }
                else:
                    return {
                        'code':500,
                        'detail':"Error insert docs"
                    }

            else:
                return {
                    'code':300,
                    'detail':"in store  or repair"
                }
        else:
            return {
                'code':400,
                'detail':"no assets_id"
            }
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi import APIRouter, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import Required
from src.models.user import User, UserInDB, UserReg
import json
import pymysql
import time
import requests


import bcrypt
import datetime
import secrets

router = APIRouter(
    prefix="/users",
    tags=["User Authentication"],
    responses={404: {"description": "Not found"}},
)
now =  time.strftime('%Y-%m-%d %H:%M:%S')
salt = b'$2b$12$k4djwBIfITqM5a4gV5Iu3.'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

db_con = pymysql.connect(host='34.87.30.13', user='root', password='Ops2022', db='test_assets')

def db_connect():
    global db_con
    if not db_con.open:
        db_con = pymysql.connect(host='34.87.30.13', user='root', password='1593578', db='ctcassetV2')
    return db_con

def hash_password(password: str):
    hashed = bcrypt.hashpw(password.encode('ascii'), salt)
    return hashed

def db_user_get(username):
    db_con = db_connect()
    with db_con.cursor() as cursor:
        sql = "SELECT username, password, fristname, lastname,privilege,enabled,user_id_agency,name_agency,user_id_branch,name_branch,rule,id FROM users"
        sql = sql + " JOIN agency ON user_id_agency = id_agency JOIN branch ON user_id_branch = id_branch"
        sql = sql + " WHERE username = '{}'".format(username)
        cursor.execute(sql)
        if cursor.rowcount > 0:
            rowdata = cursor.fetchone()
            user = { 
                'username_id':rowdata[11],
                'username': rowdata[0],
                'hashed_password': rowdata[1],
                'first_name': rowdata[2],
                'last_name': rowdata[3],
                'role': rowdata[4],
                'enabled':rowdata[5],
                'agency_id':rowdata[6],
                'name_agency':rowdata[7],
                'branch_id':rowdata[8],
                'branch_name':rowdata[9],
                'rule':rowdata[10]

                
            }
            return user

def db_token_get(token):
    db_con = db_connect()
    with db_con.cursor() as cursor:
        sql = "SELECT token, username, created_token, expire_token FROM tokens"
        sql = sql + " WHERE token = '{}'".format(token)
        cursor.execute(sql)
        if cursor.rowcount > 0:
            rowdata = cursor.fetchone()
            data_dict = {
                'token': rowdata[0],
                'username': rowdata[1],
                'created': rowdata[2],
                'expire': rowdata[3]
            }
            return data_dict

def db_token_get_from_user(username):
    db_con = db_connect()
    with db_con.cursor() as cursor:
        sql = "SELECT token, username, created_token, expire_token FROM tokens"
        sql = sql + " WHERE username = '{}'".format(username)
        cursor.execute(sql)
        if cursor.rowcount > 0:
            rowdata = cursor.fetchone()
            data_dict = {
                'token': rowdata[0],
                'username': rowdata[1],
                'created': rowdata[2],
                'expire': rowdata[3]
            }
            return data_dict

def db_token_add(username, token):
    now = datetime.datetime.now()
    expire = now + datetime.timedelta(days=90)
    db_con = db_connect()
    with db_con.cursor() as cursor:
        sql = "INSERT INTO tokens (token, username, created_token, expire_token)"
        sql = sql + "  VALUES ('{}', '{}', '{}', '{}')".format(
            token, username, 
            now.strftime('%Y-%m-%d %H:%M:%S'), 
            expire.strftime('%Y-%m-%d %H:%M:%S'))
        print(sql)
        cursor.execute(sql)
        db_con.commit()
        data_dict = {
            'token': token,
            'username': username,
            'created': now,
            'expire': expire
        }
        return data_dict

def token_is_valid(token):
    db_con = db_connect()
    with db_con.cursor() as cursor:
        sql = "SELECT token, created_token, expire_token FROM tokens"
        sql = sql + " WHERE token = '{}'".format(token)
        cursor.execute(sql)
        rowdata = cursor.fetchone()
        expire_time = rowdata[2]
        now = datetime.datetime.now()
        if now > expire_time:
            return False
        else:
            return True

def token_generate():
    token = secrets.token_hex(32)
    return token

def get_user(db, token: str):
    for user in db:
        if db[user]['token'] == token:
            user_dict = db[user]
            print(user_dict)
            return UserInDB(**user_dict)

def token_decode(token):
    data = db_token_get(token)
    if data:
        user_dict = db_user_get(data['username'])
        return User(**user_dict)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = token_decode(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.enabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


   
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db_user_get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    #user = UserInDB(**user_dict)

    if not hash_password(form_data.password) == user['hashed_password'].encode('ascii'):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = db_token_get_from_user(user['username'])
    if not token:
        token = token_generate()
        token = db_token_add(user['username'], token)

    return {"access_token": token['token'], "token_type": "bearer"}





@router.post("/regsiter")
async def regsiter(username:str,password:str,fristname:str,lastname:str,agency_id:int):
    print(password)
    con = db_connect()
    with con.cursor() as cur:
        sqlck1 = "select id from users where username = %s"
        try:
            cur.execute(sqlck1,(username))
            con.commit()
        except pymysql.Error as e: 
            print(f"Error: {e}")
            return {
                'code': 500,
                'detail': f"Error: {e}"
            }
        else:
            if cur.rowcount > 0 :
                return {
                    'code':300,
                    'detail':"existed"
                }
            else:
                en_pass = hash_password(password)
                pass_en = en_pass.decode('ascii')
                sqlinsert="insert into users (username,password,fristname,lastname,privilege,user_id_agency,enabled) values (%s,%s,%s,%s,31,%s,1)"
                
                try:
                    cur.execute(sqlinsert,(username,pass_en,fristname,lastname,int(agency_id)))
                    con.commit()
                except pymysql.Error as e:
                    print(f"Error: {e}")
                    return {
                        'code': 500,
                        'detail': f"Error: {e}"
                    }
                else:
                    return {
                        'code':200,
                        'detail':'success'
                    }
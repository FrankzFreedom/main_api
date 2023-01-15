from pydantic import BaseModel, Field
from typing import Optional
from typing import Union

class User(BaseModel):
    username: str
    
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    role: Union[str, None] = None
    enabled: Union[bool, None] = None
    agency_id: Union[str,None] = None
    name_agency: Union[str,None] = None
    branch_id: Union[str,None] = None
    branch_name: Union[str,None] = None
    rule: Union[str,None] = None
    username_id:Union[str,None] = None
    

class UserReg(BaseModel):
    username: str
    password: str
    email: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None

class UserInDB(User):
    hashed_password: str
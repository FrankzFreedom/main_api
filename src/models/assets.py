from pydantic import BaseModel, Field

class assets(BaseModel):
    serial:str
    id_model:str
    id_branch:str
    remark:str
    macaddress:str
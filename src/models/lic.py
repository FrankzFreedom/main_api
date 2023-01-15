from pydantic import BaseModel, Field

class keys(BaseModel):
    id_lic : str
    lic_keys : list

class keysadd(BaseModel):                              # Class รับค่าต่างๆ
    lic_dt_name :str                                # รับค่า Name
    lic_dt_type :str                                # รับค่า Type
    expire : str                                    # รับค่า Expire (วันหมดอายุ)
    lic_keys : list                                 # รับค่า Key ของ License
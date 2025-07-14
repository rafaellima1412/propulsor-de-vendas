from typing import Optional

from pydantic import BaseModel

class UserMinimal(BaseModel):
    id: int
    full_name: str

class TimeBase(BaseModel):
    name: str
    gerente_id: int
    coo_id: int

class TimeCreate(TimeBase):
    pass

class TimeOut(TimeBase):
    id: int
    name: str
    gerente: Optional[UserMinimal] = None
    coo: Optional[UserMinimal] = None
    class Config:
        from_attributes = True

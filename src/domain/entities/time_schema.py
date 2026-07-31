from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.domain.entities.local_schema import  LocalResumoSchema


class UserMinimal(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)

class TimeBase(BaseModel):
    name: str
    local: Optional[LocalResumoSchema] = None
    gerente_id: int
    coo_id: int

    model_config = ConfigDict(from_attributes=True)

class TimeCreate(TimeBase):
    pass

class TimeOut(TimeBase):
    id: int
    gerente: Optional[UserMinimal] = None
    coo: Optional[UserMinimal] = None
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class TimeUpdate(BaseModel):
    name: Optional[str] = None
    gerente_id: Optional[int] = None
    coo_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
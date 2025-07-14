from pydantic import BaseModel, constr, Field
from typing import List, Optional

from src.domain.entities.sales import VendaSchema
from src.domain.entities.time_schema import TimeOut


class UserBase(BaseModel):
    username: str
    full_name: str # "gerente", "coo", "colaborador"
    cpf: constr(min_length=11, max_length=14)

class UserCreate(UserBase):
    password: str
    time_id: Optional[int] = None

class UserOut(UserBase):
    id: int
    # mantem no para o jinja mas no banco e full-name
    nome: str = Field(..., alias="full_name")
    time_id: Optional[int] = None
    time: Optional[TimeOut] = None
    campanhas: List[VendaSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True

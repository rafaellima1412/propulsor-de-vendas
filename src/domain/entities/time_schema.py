from pydantic import BaseModel, ConfigDict

from src.domain.entities.local_schema import LocalResumoSchema


class UserMinimal(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class TimeBase(BaseModel):
    name: str
    local: LocalResumoSchema | None = None
    gerente_id: int
    coo_id: int

    model_config = ConfigDict(from_attributes=True)


class TimeCreate(TimeBase):
    pass


class TimeOut(TimeBase):
    id: int
    gerente: UserMinimal | None = None
    coo: UserMinimal | None = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimeUpdate(BaseModel):
    name: str | None = None
    gerente_id: int | None = None
    coo_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

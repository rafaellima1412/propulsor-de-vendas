from pydantic import BaseModel, ConfigDict, Field, constr

from src.domain.entities.campaign import Campaign


class UserBase(BaseModel):
    username: str
    full_name: str  # "coordenador", "gerente", "colaborador"
    cpf: constr(min_length=11, max_length=14)


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    full_name: str | None = None
    status: str | None = None
    descricao: str | None = None
    campanhas: list[Campaign] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

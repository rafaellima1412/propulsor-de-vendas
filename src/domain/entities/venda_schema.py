from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.domain.enums.enums import PlanoInternet, StatusVenda


class UserMinimal(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class CampanhaMinimal(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class VendaOut(BaseModel):
    id: int
    plano: PlanoInternet
    status: StatusVenda
    descricao: str | None = None
    cpf_vendedor: str
    data_criacao: datetime | None = None

    usuario: UserMinimal | None = None
    campanha: CampanhaMinimal | None = None

    model_config = ConfigDict(from_attributes=True)
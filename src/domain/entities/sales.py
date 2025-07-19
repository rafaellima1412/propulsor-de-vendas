from datetime import datetime, timezone

from pydantic import BaseModel

from src.domain.enums.enums import PlanoInternet, StatusVenda


class VendaSchema(BaseModel):
    plano: PlanoInternet
    status: StatusVenda
    area: str
    descricao: str
    data_criacao: datetime = datetime.now(timezone.utc)

    class Config:
        from_attributes = True
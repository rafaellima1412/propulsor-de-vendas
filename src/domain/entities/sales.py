from datetime import datetime, timezone

from pydantic import BaseModel, Field, ConfigDict

from src.domain.enums.enums import PlanoInternet, StatusVenda


class VendaSchema(BaseModel):
    plano: PlanoInternet
    status: StatusVenda
    area: str
    descricao: str
    data_criacao: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)
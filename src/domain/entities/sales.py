from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums.enums import PlanoInternet, StatusVenda


class VendaSchema(BaseModel):
    plano: PlanoInternet
    status: StatusVenda
    descricao: str
    data_criacao: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(from_attributes=True)

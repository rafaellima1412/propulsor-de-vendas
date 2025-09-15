
from typing import Optional
from pydantic import Field

from pydantic import BaseModel, ConfigDict


class Coordenadas(BaseModel):
    latitude: float = Field(..., description="Latitude do local")
    longitude: float = Field(..., description="Longitude do local")

    model_config = ConfigDict(from_attributes=True)

class LocalResumoSchema(BaseModel):
    id: Optional[int]
    nome: str

    model_config = ConfigDict(from_attributes=True)

class LocalSchema(BaseModel):
    id: Optional[int] = Field(None, description="ID do local")
    nome: str = Field(..., description="Nome do local")
    coordenadas: Coordenadas

    model_config = ConfigDict(from_attributes=True)
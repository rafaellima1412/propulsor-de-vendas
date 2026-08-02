from pydantic import BaseModel, ConfigDict, Field


class Coordenadas(BaseModel):
    latitude: float = Field(..., description="Latitude do local")
    longitude: float = Field(..., description="Longitude do local")

    model_config = ConfigDict(from_attributes=True)


class LocalResumoSchema(BaseModel):
    id: int | None
    nome: str

    model_config = ConfigDict(from_attributes=True)


class LocalSchema(BaseModel):
    id: int | None = Field(None, description="ID do local")
    nome: str = Field(..., description="Nome do local")
    coordenadas: Coordenadas

    model_config = ConfigDict(from_attributes=True)


class LocalCreate(BaseModel):
    nome: str = Field(..., description="Nome do local")
    coordenadas: Coordenadas

    model_config = ConfigDict(from_attributes=True)


class LocalUpdate(BaseModel):
    nome: str | None = Field(None, description="Nome do local")
    coordenadas: Coordenadas | None = None

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel


class AssociarColaboradorRequest(BaseModel):
    usuario_id: int


class AssociarCoordenadorRequest(BaseModel):
    coordenador_id: int

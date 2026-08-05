from pydantic import BaseModel


class AssociarColaboradorRequest(BaseModel):
    usuario_id: int
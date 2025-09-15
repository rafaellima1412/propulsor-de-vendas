from pydantic import BaseModel

from src.domain.enums.enums import PlanoInternet, StatusVenda


class VendaCreateDTO(BaseModel):
    plano: PlanoInternet
    status: StatusVenda
    descricao: str
    cpf_vendedor: int
    campanha_id: int
    usuario_id: int

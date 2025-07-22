from pydantic import BaseModel

class CarteiraFinanceiraDTO(BaseModel):
    usuario_id: int
    saldo_atual: float
    total_receitas: float
    total_despesas: float
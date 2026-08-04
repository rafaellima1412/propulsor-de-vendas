from pydantic import BaseModel


class CarteiraOut(BaseModel):
    usuario_id: int

    # Resultado
    saldo_estimado: float
    vendas_por_status: dict[str, int]
    vendas_por_plano: dict[str, int]

    # Esforço
    total_campanhas: int
    total_vendas_registradas: int
    taxa_conversao: float  # 0.0 a 1.0 — vendas com status "vendido" / total registrado


class CarteiraAgregadaOut(BaseModel):
    """Mesma ideia da CarteiraOut, mas somando vários colaboradores — usada
    pela carteira do time (gerente) e pela carteira geral (coordenador)."""

    total_colaboradores: int

    saldo_estimado: float
    vendas_por_status: dict[str, int]
    vendas_por_plano: dict[str, int]

    total_campanhas: int
    total_vendas_registradas: int
    taxa_conversao: float
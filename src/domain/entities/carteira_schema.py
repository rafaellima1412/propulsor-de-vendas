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


class RankingVendedorOut(BaseModel):
    """Uma linha do ranking de vendedores — quantas vendas (status
    'vendido') cada colaborador fechou."""

    usuario_id: int
    full_name: str
    total_vendido: int


class MapaCalorPontoOut(BaseModel):
    """Um ponto no mapa de calor de vendas — total de vendas fechadas na
    região desse local."""

    local_id: int
    nome: str
    latitude: float
    longitude: float
    total_vendas: int
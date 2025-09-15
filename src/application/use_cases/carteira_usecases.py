from src.application.repositories.ivenda_repository import IVendaRepository


class CarteiraUseCase:
    def __init__(self, venda_repo: IVendaRepository):
        self.venda_repo = venda_repo

    def calcular_carteira(self, usuario_id: int) -> float:
        vendas = self.venda_repo.list_by_usuario_id(usuario_id)
        return sum(v.valor_comissao for v in vendas if v.status == "vendido")

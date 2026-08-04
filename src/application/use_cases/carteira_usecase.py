from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.application.repositories.ivenda_repository import IVendaRepository
from src.domain.constants.comissoes import COMISSAO_POR_PLANO
from src.domain.entities.carteira_schema import CarteiraOut
from src.domain.enums.enums import StatusVenda


class CarteiraUseCase:
    """Monta a carteira do colaborador (resultado + esforço) a partir de
    dados que já existem de verdade no sistema — vendas registradas e
    campanhas recebidas. Não depende de nenhuma tabela ou coluna nova."""

    def __init__(self, venda_repo: IVendaRepository, campanha_repo: ICampanhaRepository):
        self.venda_repo = venda_repo
        self.campanha_repo = campanha_repo

    def calcular_carteira(self, usuario_id: int) -> CarteiraOut:
        vendas = self.venda_repo.get_by_usuario_ids([usuario_id])
        campanhas = self.campanha_repo.list_by_usuario_id(usuario_id)

        vendas_por_status = {status.value: 0 for status in StatusVenda}
        vendas_por_plano: dict[str, int] = {}
        saldo_estimado = 0.0

        for venda in vendas:
            status_valor = venda.status.value if hasattr(venda.status, "value") else venda.status
            vendas_por_status[status_valor] = vendas_por_status.get(status_valor, 0) + 1

            if status_valor == StatusVenda.vendido.value:
                plano_valor = venda.plano.value if hasattr(venda.plano, "value") else venda.plano
                vendas_por_plano[plano_valor] = vendas_por_plano.get(plano_valor, 0) + 1
                saldo_estimado += COMISSAO_POR_PLANO.get(plano_valor, 0.0)

        total_vendas_registradas = len(vendas)
        total_vendido = vendas_por_status.get(StatusVenda.vendido.value, 0)
        taxa_conversao = (total_vendido / total_vendas_registradas) if total_vendas_registradas else 0.0

        return CarteiraOut(
            usuario_id=usuario_id,
            saldo_estimado=saldo_estimado,
            vendas_por_status=vendas_por_status,
            vendas_por_plano=vendas_por_plano,
            total_campanhas=len(campanhas),
            total_vendas_registradas=total_vendas_registradas,
            taxa_conversao=round(taxa_conversao, 4),
        )
from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.application.repositories.iuser_repository import IUserRepository
from src.application.repositories.ivenda_repository import IVendaRepository
from src.domain.constants.comissoes import COMISSAO_POR_PLANO
from src.domain.entities.carteira_schema import (
    CarteiraAgregadaOut,
    CarteiraOut,
    MapaCalorPontoOut,
    RankingVendedorOut,
)
from src.domain.enums.enums import StatusVenda


class CarteiraUseCase:
    def __init__(self, venda_repo: IVendaRepository, campanha_repo: ICampanhaRepository, user_repo: IUserRepository):
        self.venda_repo = venda_repo
        self.campanha_repo = campanha_repo
        self.user_repo = user_repo

    def calcular_carteira(self, usuario_id: int) -> CarteiraOut:
        vendas = self.venda_repo.get_by_usuario_ids([usuario_id])
        campanhas = self.campanha_repo.list_by_usuario_id(usuario_id)
        resumo = self._resumir_vendas(vendas)

        return CarteiraOut(usuario_id=usuario_id, total_campanhas=len(campanhas), **resumo)

    def calcular_carteira_time(self, coordenador_id: int) -> CarteiraAgregadaOut:
        colaboradores = self.user_repo.get_colaboradores_by_coordenador(coordenador_id)
        colaborador_ids = [c.id for c in colaboradores]

        vendas = self.venda_repo.get_by_usuario_ids(colaborador_ids)
        campanhas = self.campanha_repo.list_by_coordenador_id(coordenador_id)
        resumo = self._resumir_vendas(vendas)

        return CarteiraAgregadaOut(
            total_colaboradores=len(colaborador_ids), total_campanhas=len(campanhas), **resumo
        )

    def calcular_carteira_geral(self) -> CarteiraAgregadaOut:
        colaboradores = self.user_repo.get_by_role("colaborador")
        colaborador_ids = [c.id for c in colaboradores]

        vendas = self.venda_repo.get_by_usuario_ids(colaborador_ids)
        campanhas = self.campanha_repo.get_all()
        resumo = self._resumir_vendas(vendas)

        return CarteiraAgregadaOut(
            total_colaboradores=len(colaborador_ids), total_campanhas=len(campanhas), **resumo
        )

    def ranking_time(self, coordenador_id: int) -> list[RankingVendedorOut]:
        colaboradores = self.user_repo.get_colaboradores_by_coordenador(coordenador_id)
        return self._ranking(colaboradores)

    def ranking_geral(self) -> list[RankingVendedorOut]:
        colaboradores = self.user_repo.get_by_role("colaborador")
        return self._ranking(colaboradores)

    def mapa_calor_time(self, coordenador_id: int) -> list[MapaCalorPontoOut]:
        return [MapaCalorPontoOut(**ponto) for ponto in self.venda_repo.mapa_calor(coordenador_id)]

    def mapa_calor_geral(self) -> list[MapaCalorPontoOut]:
        return [MapaCalorPontoOut(**ponto) for ponto in self.venda_repo.mapa_calor()]

    def _ranking(self, colaboradores: list) -> list[RankingVendedorOut]:
        colaborador_ids = [c.id for c in colaboradores]
        contagem = self.venda_repo.ranking_por_usuario(colaborador_ids)

        ranking = [
            RankingVendedorOut(usuario_id=c.id, full_name=c.full_name, total_vendido=contagem.get(c.id, 0))
            for c in colaboradores
        ]
        ranking.sort(key=lambda r: r.total_vendido, reverse=True)
        return ranking

    def _resumir_vendas(self, vendas: list) -> dict:
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

        return {
            "saldo_estimado": saldo_estimado,
            "vendas_por_status": vendas_por_status,
            "vendas_por_plano": vendas_por_plano,
            "total_vendas_registradas": total_vendas_registradas,
            "taxa_conversao": round(taxa_conversao, 4),
        }
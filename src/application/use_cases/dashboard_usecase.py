# application/usecases/dashboard_usecase.py
import calendar

from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.application.repositories.ICarteiraRepository import ICarteiraRepository
from src.application.repositories.ivenda_repository import IVendaRepository


class DashboardUseCase:
    def __init__(
        self, campanha_repo: ICampanhaRepository, venda_repo: IVendaRepository, carteira_repo: ICarteiraRepository
    ):
        self.campanha_repo = campanha_repo
        self.venda_repo = venda_repo
        self.carteira_repo = carteira_repo

    def get_dashboard_data(self, user_id: int, time_id: int) -> dict:
        campanhas = self.campanha_repo.list_by_time_id(time_id)
        # vendas = self.venda_repo.list_vendas_by_usuario_id(user_id)
        # carteira = self.carteira_repo.list_carteira_by_usuario_id(user_id)

        vendas_por_plano = self.venda_repo.contagem_por_plano(user_id)
        vendas_por_mes = self.venda_repo.contagem_por_mes(user_id)

        planos_labels = list(vendas_por_plano.keys())
        planos_data = list(vendas_por_plano.values())
        planos_cores = ["#3498db", "#2ecc71", "#f1c40f", "#e74c3c", "#9b59b6"][: len(planos_labels)]

        mes_labels = [f"{calendar.month_abbr[int(mes)].capitalize()}/{int(ano)}" for ano, mes in vendas_por_mes.keys()]
        mes_data = list(vendas_por_mes.values())

        return {
            "campanhas": campanhas,
            "dashboard_data": {
                "vendas_por_plano": vendas_por_plano,
                "area": {
                    "labels": planos_labels,
                    "data": planos_data,
                    "colors": planos_cores,
                },
                "finance": {
                    "labels": mes_labels,
                    "data": mes_data,
                },
            },
            "planos_cores": planos_cores,
        }

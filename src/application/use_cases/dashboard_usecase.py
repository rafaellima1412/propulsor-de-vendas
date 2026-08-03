import calendar
from typing import Any

from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.application.repositories.iuser_repository import IUserRepository
from src.application.repositories.ivenda_repository import IVendaRepository

class DashboardUseCase:
    def __init__(
        self, campanha_repo: ICampanhaRepository, venda_repo: IVendaRepository, user_repo: IUserRepository
    ):
        self.campanha_repo = campanha_repo
        self.venda_repo = venda_repo
        # self.carteira_repo = carteira_repo
        self.user_repo = user_repo

    def get_dashboard_data(self, user: dict[str, Any]) -> dict:
        if user["role"] == "colaborador": 
            campanhas = self.campanha_repo.list_by_usuario_id(user["id"]) 
            vendas_por_plano = self.venda_repo.contagem_por_plano(user["id"])
            vendas_por_mes = self.venda_repo.contagem_por_mes(user["id"])

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
        if user["role"] == "coordenador": 
                    campanhas = self.campanha_repo.get_all() 
                    vendas_por_plano = self.venda_repo.contagem_por_plano_all()
                    vendas_por_mes = self.venda_repo.contagem_por_mes_all()
        
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
        if user["role"] == "gerente":
                    times = self.user_repo.get_times_ids_by_gerente(user["id"])
                    campanhas = self.campanha_repo.list_by_time_ids(times) 
                    colaboradores = self.user_repo.get_colaboradores_by_gerente(user["id"])
                    colaborador_ids = [colaborador.id for colaborador in colaboradores]
                    vendas_por_plano = self.venda_repo.contagem_por_plano(colaborador_ids)
                    vendas_por_mes = self.venda_repo.contagem_por_mes(colaborador_ids)
        
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
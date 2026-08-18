from unittest.mock import MagicMock

import pytest

from src.application.use_cases.dashboard_usecase import DashboardUseCase

pytestmark = pytest.mark.unit


@pytest.fixture
def campanha_repo():
    return MagicMock()


@pytest.fixture
def venda_repo():
    return MagicMock()


@pytest.fixture
def user_repo():
    return MagicMock()


@pytest.fixture
def usecase(campanha_repo, venda_repo, user_repo):
    return DashboardUseCase(campanha_repo=campanha_repo, venda_repo=venda_repo, user_repo=user_repo)


# --- coordenador: dono da visão "empresa toda", sem filtro por usuário/time ---


def test_coordenador_usa_metodos_sem_filtro(usecase, campanha_repo, venda_repo, user_repo):
    campanha_repo.get_all.return_value = ["campanha-1", "campanha-2"]
    venda_repo.contagem_por_plano_all.return_value = {"1GB": 10, "2GB": 5}
    venda_repo.contagem_por_mes_all.return_value = {(2026, 1): 7, (2026, 2): 8}

    result = usecase.get_dashboard_data({"id": 1, "role": "gerente"})

    campanha_repo.get_all.assert_called_once_with()
    venda_repo.contagem_por_plano_all.assert_called_once_with()
    venda_repo.contagem_por_mes_all.assert_called_once_with()
    assert result["campanhas"] == ["campanha-1", "campanha-2"]


def test_coordenador_nao_usa_metodos_escopados_por_usuario_ou_time(usecase, campanha_repo, venda_repo, user_repo):
    """O ponto central de 'coordenador é só get all': nenhum método com filtro
    (por usuário, por time, por gerente) pode ser chamado nesse branch."""
    campanha_repo.get_all.return_value = []
    venda_repo.contagem_por_plano_all.return_value = {}
    venda_repo.contagem_por_mes_all.return_value = {}

    usecase.get_dashboard_data({"id": 1, "role": "gerente"})

    campanha_repo.list_by_usuario_id.assert_not_called()
    campanha_repo.list_by_coordenador_id.assert_not_called()
    venda_repo.contagem_por_plano.assert_not_called()
    venda_repo.contagem_por_mes.assert_not_called()
    user_repo.get_colaboradores_by_coordenador.assert_not_called()


def test_coordenador_monta_labels_e_dados_do_grafico_de_planos(usecase, campanha_repo, venda_repo):
    campanha_repo.get_all.return_value = []
    venda_repo.contagem_por_plano_all.return_value = {"1GB": 10, "2GB": 5, "10GB": 2}
    venda_repo.contagem_por_mes_all.return_value = {}

    result = usecase.get_dashboard_data({"id": 1, "role": "gerente"})
    area = result["dashboard_data"]["area"]

    assert area["labels"] == ["1GB", "2GB", "10GB"]
    assert area["data"] == [10, 5, 2]
    assert "colors" not in area
    assert "planos_cores" not in result


def test_coordenador_monta_labels_de_mes_formatadas(usecase, campanha_repo, venda_repo):
    campanha_repo.get_all.return_value = []
    venda_repo.contagem_por_plano_all.return_value = {}
    venda_repo.contagem_por_mes_all.return_value = {(2026, 1): 3, (2026, 12): 9}

    result = usecase.get_dashboard_data({"id": 1, "role": "gerente"})
    finance = result["dashboard_data"]["finance"]

    assert finance["labels"] == ["Jan/2026", "Dec/2026"]
    assert finance["data"] == [3, 9]


def test_coordenador_com_dados_vazios_nao_quebra(usecase, campanha_repo, venda_repo):
    """Regressão do bug real: antes desses métodos existirem nos repositórios,
    esse branch quebrava com AttributeError em qualquer chamada, banco vazio ou não."""
    campanha_repo.get_all.return_value = []
    venda_repo.contagem_por_plano_all.return_value = {}
    venda_repo.contagem_por_mes_all.return_value = {}

    result = usecase.get_dashboard_data({"id": 1, "role": "gerente"})

    assert result["campanhas"] == []
    assert result["dashboard_data"]["area"]["labels"] == []
    assert result["dashboard_data"]["finance"]["labels"] == []


# --- comparativo rápido com os outros dois papéis, pra travar que não regridem ---


def test_colaborador_usa_metodos_escopados_por_usuario(usecase, campanha_repo, venda_repo):
    campanha_repo.list_by_usuario_id.return_value = []
    venda_repo.contagem_por_plano.return_value = {}
    venda_repo.contagem_por_mes.return_value = {}

    usecase.get_dashboard_data({"id": 42, "role": "colaborador"})

    campanha_repo.list_by_usuario_id.assert_called_once_with(42)
    venda_repo.contagem_por_plano.assert_called_once_with(42)
    venda_repo.contagem_por_mes.assert_called_once_with(42)
    campanha_repo.get_all.assert_not_called()


def test_coordenador_role_usa_metodos_escopados_por_campanha(usecase, campanha_repo, venda_repo, user_repo):
    user_repo.get_colaboradores_by_coordenador.return_value = []
    campanha_repo.list_by_coordenador_id.return_value = []
    venda_repo.contagem_por_plano.return_value = {}
    venda_repo.contagem_por_mes.return_value = {}

    usecase.get_dashboard_data({"id": 7, "role": "coordenador"})

    user_repo.get_colaboradores_by_coordenador.assert_called_once_with(7)
    campanha_repo.list_by_coordenador_id.assert_called_once_with(7)
    campanha_repo.get_all.assert_not_called()
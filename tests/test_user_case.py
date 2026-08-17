from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.use_cases.user_usecase import UserUseCase
from src.infra.database.models.user_model import UserModel

pytestmark = pytest.mark.unit


def make_dto(**overrides) -> UserCreateDTO:
    data = dict(
        username="ana.silva",
        full_name="Ana Silva",
        role="colaborador",
        cpf="11144477735",
        hashed_password="hashed-value",
    )
    data.update(overrides)
    return UserCreateDTO(**data)


@pytest.fixture
def user_repo():
    repo = MagicMock()
    repo.get_by_cpf.return_value = None
    repo.get_by_username.return_value = None
    return repo


@pytest.fixture
def time_repo():
    return MagicMock()


@pytest.fixture
def usecase(user_repo, time_repo):
    return UserUseCase(user_repo=user_repo, time_repo=time_repo)


def test_create_user_rejects_duplicate_cpf(usecase, user_repo):
    user_repo.get_by_cpf.return_value = UserModel(id=1, cpf="11144477735")

    with pytest.raises(HTTPException) as exc_info:
        usecase.create_user(make_dto())

    assert exc_info.value.status_code == 400
    assert "CPF" in exc_info.value.detail
    user_repo.create.assert_not_called()


def test_create_user_rejects_duplicate_username(usecase, user_repo):
    user_repo.get_by_username.return_value = UserModel(id=1, username="ana.silva")

    with pytest.raises(HTTPException) as exc_info:
        usecase.create_user(make_dto())

    assert exc_info.value.status_code == 400
    assert "Username" in exc_info.value.detail
    user_repo.create.assert_not_called()


def test_create_colaborador_without_time_is_allowed(usecase, user_repo):
    user_repo.create.return_value = UserModel(id=1, username="ana.silva", role="colaborador")

    result = usecase.create_user(make_dto(role="colaborador"))

    assert result.username == "ana.silva"
    user_repo.create.assert_called_once()
    user_repo.update.assert_not_called()


def test_create_gerente_without_team_info_raises(usecase, user_repo):
    user_repo.create.return_value = UserModel(id=1, username="ana.silva", role="coordenador")

    with pytest.raises(HTTPException) as exc_info:
        usecase.create_user(make_dto(role="coordenador"))

    assert exc_info.value.status_code == 400
    assert "Time" in exc_info.value.detail


def test_create_gerente_with_new_team_creates_it(usecase, user_repo, time_repo):
    created_user = UserModel(id=1, username="ana.silva", role="coordenador")
    user_repo.create.return_value = created_user
    time_repo.get_by_name.return_value = None
    time_repo.create.return_value = MagicMock(id=42)

    usecase.create_user(make_dto(role="coordenador", novo_time="Time Alpha"))

    time_repo.create.assert_called_once()
    user_repo.update.assert_called_once()
    assert created_user.time_id == 42


def test_create_gerente_with_existing_team_id_links_it(usecase, user_repo, time_repo):
    created_user = UserModel(id=1, username="ana.silva", role="coordenador")
    user_repo.create.return_value = created_user

    usecase.create_user(make_dto(role="coordenador", time_existente_id=7))

    assert created_user.time_id == 7
    user_repo.update.assert_called_once()
    time_repo.create.assert_not_called()


def test_create_coordenador_requires_subordinado_id(usecase, user_repo):
    user_repo.create.return_value = UserModel(id=1, username="ana.silva", role="gerente")

    with pytest.raises(HTTPException) as exc_info:
        usecase.create_user(make_dto(role="gerente"))

    assert exc_info.value.status_code == 400
    assert "Coordenador" in exc_info.value.detail


def test_create_coordenador_with_invalid_subordinado_raises_404(usecase, user_repo):
    user_repo.create.return_value = UserModel(id=1, username="ana.silva", role="gerente")
    user_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        usecase.create_user(make_dto(role="gerente", subordinado_id=99))

    assert exc_info.value.status_code == 404


def test_list_users_delegates_to_repository(usecase, user_repo):
    user_repo.get_all.return_value = [UserModel(id=1), UserModel(id=2)]

    result = usecase.list_users()

    assert len(result) == 2
    user_repo.get_all.assert_called_once()
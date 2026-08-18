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
def usecase(user_repo):
    return UserUseCase(user_repo=user_repo)


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


def test_create_colaborador_is_allowed(usecase, user_repo):
    user_repo.create.return_value = UserModel(id=1, username="ana.silva", role="colaborador")

    result = usecase.create_user(make_dto(role="colaborador"))

    assert result.username == "ana.silva"
    user_repo.create.assert_called_once()


def test_create_coordenador_is_allowed(usecase, user_repo):
    user_repo.create.return_value = UserModel(id=1, username="ana.silva", role="coordenador")

    result = usecase.create_user(make_dto(role="coordenador"))

    assert result.username == "ana.silva"
    user_repo.create.assert_called_once()


def test_create_gerente_is_allowed(usecase, user_repo):
    user_repo.create.return_value = UserModel(id=1, username="ana.silva", role="gerente")

    result = usecase.create_user(make_dto(role="gerente"))

    assert result.username == "ana.silva"
    user_repo.create.assert_called_once()


def test_list_users_delegates_to_repository(usecase, user_repo):
    user_repo.get_all.return_value = [UserModel(id=1), UserModel(id=2)]

    result = usecase.list_users()

    assert len(result) == 2
    user_repo.get_all.assert_called_once()

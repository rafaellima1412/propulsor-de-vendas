# application/interfaces/user_repository_interface.py
from abc import ABC, abstractmethod

from src.application.dtos.user_create_dto import UserCreateDTO
from src.infra.database.models.user_model import UserModel


class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: UserCreateDTO) -> UserModel:
        pass

    @abstractmethod
    def get_all(self) -> list[UserModel]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> UserModel | None:
        pass

    @abstractmethod
    def get_by_cpf(self, cpf: str) -> UserModel | None:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> UserModel | None:
        pass

    def update(self, user: UserModel) -> UserModel:
        """Atualiza um usuário existente no banco de dados."""
        raise NotImplementedError

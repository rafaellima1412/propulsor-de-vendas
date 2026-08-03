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
    @abstractmethod
    def update(self, user: UserModel) -> UserModel:
        pass
    @abstractmethod
    def get_by_role(self, role: str) -> list[UserModel]:
        pass
    @abstractmethod
    def get_gerentes_by_coo(self, coo_id: int) -> list[UserModel]:
        pass
    @abstractmethod
    def get_times_ids_by_gerente(self, gerente_id: int) -> list[int]:
        pass
    @abstractmethod
    def get_colaboradores_by_gerente(self, gerente_id: int) -> list[UserModel]:
        pass
    
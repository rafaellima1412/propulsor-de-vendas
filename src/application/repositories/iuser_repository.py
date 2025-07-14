# application/interfaces/user_repository_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional
from src.application.dtos.user_create_dto import UserCreateDTO
from src.infra.database.models.user_model import UserModel

class IUserRepository(ABC):

    @abstractmethod
    def create(self, user: UserCreateDTO) -> UserModel:
        pass

    @abstractmethod
    def get_all(self) -> List[UserModel]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_by_cpf(self, cpf: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserModel]:
        pass

    def update(self, user: UserModel) -> UserModel:
        """Atualiza um usuário existente no banco de dados."""
        raise NotImplementedError
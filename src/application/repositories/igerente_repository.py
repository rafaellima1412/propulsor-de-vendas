from abc import ABC, abstractmethod

from src.application.dtos.user_create_dto import UserCreateDTO
from src.domain.entities.user_schema import UserBase

# from src.domain.entities.gerente_schema import GerenteCreate, GerenteBase


class IGerenteRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[UserBase]: ...

    @abstractmethod
    def get_by_id(self, id: int) -> UserBase | None: ...

    @abstractmethod
    def create(self, gerente: UserCreateDTO) -> UserCreateDTO: ...

    @abstractmethod
    def update(self, gerente: UserBase) -> UserBase: ...

    @abstractmethod
    def delete(self, id: int) -> None: ...

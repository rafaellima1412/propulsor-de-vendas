from abc import ABC, abstractmethod
from typing import List, Optional

from src.application.dtos.user_create_dto import UserCreateDTO
from src.domain.entities.user_schema import UserBase


# from src.domain.entities.gerente_schema import GerenteCreate, GerenteBase


class IGerenteRepository(ABC):

    @abstractmethod
    def list_all(self) -> List[UserBase]: ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[UserBase]: ...

    @abstractmethod
    def create(self, gerente: UserCreateDTO) -> UserCreateDTO: ...

    @abstractmethod
    def update(self, gerente: UserBase) -> UserBase: ...

    @abstractmethod
    def delete(self, id: int) -> None: ...
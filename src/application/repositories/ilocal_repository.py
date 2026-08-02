from abc import ABC, abstractmethod

from src.domain.entities.local_schema import LocalCreate, LocalSchema, LocalUpdate


class ILocalRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[LocalSchema]:
        pass

    @abstractmethod
    def get_by_id(self, local_id: int) -> LocalSchema | None:
        pass

    @abstractmethod
    def create(self, data: LocalCreate) -> LocalSchema:
        pass

    @abstractmethod
    def update(self, local_id: int, data: LocalUpdate) -> LocalSchema | None:
        pass

    @abstractmethod
    def delete(self, local_id: int) -> None:
        pass

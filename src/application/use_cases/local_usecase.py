from src.application.repositories.ilocal_repository import ILocalRepository
from src.domain.entities.local_schema import LocalCreate, LocalSchema, LocalUpdate


class LocalUseCase:
    def __init__(self, local_repository: ILocalRepository):
        self.local_repository = local_repository

    def list_all(self) -> list[LocalSchema]:
        return self.local_repository.list_all()

    def get_by_id(self, local_id: int) -> LocalSchema | None:
        return self.local_repository.get_by_id(local_id)

    def create(self, data: LocalCreate) -> LocalSchema:
        return self.local_repository.create(data)

    def update(self, local_id: int, data: LocalUpdate) -> LocalSchema | None:
        return self.local_repository.update(local_id, data)

    def delete(self, local_id: int) -> None:
        self.local_repository.delete(local_id)

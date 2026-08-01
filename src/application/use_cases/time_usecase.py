from src.application.repositories.ITimeRepository import ITimeRepository
from src.infra.database.models.time_model import TimeModel


class TimeUseCase:
    def __init__(self, time_repository: ITimeRepository):
        self.time_repository = time_repository

    def list_by_user(self, user_id: int) -> list[TimeModel]:
        return self.time_repository.list_by_user_id(user_id)

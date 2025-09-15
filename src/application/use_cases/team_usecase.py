# src/application/usecases/time_usecase.py
from typing import List, Optional
from sqlalchemy.orm import Session

from src.application.repositories.ITimeRepository import ITimeRepository
from src.domain.entities.time_schema import TimeCreate, TimeOut


class TimeUseCase:
    def __init__(self, time_repository: ITimeRepository):
        self.time_repository = time_repository

    def list_all(self) -> List[TimeOut]:
        return  self.time_repository.list_all()

    def get_time_by_id(self, time_id: int) -> Optional[TimeOut]:
        return  self.time_repository.get_by_id(time_id)

    def create_time(self, data: TimeCreate) -> TimeOut:
        return  self.time_repository.create(data)

    def update_time(self, time_id: int, data: TimeCreate) -> TimeOut:
        return  self.time_repository.update(time_id, data)

    def delete_time(self, time_id: int) -> None:
        self.time_repository.delete(time_id)

    def get_times_by_coo(self, coo_id: int) -> List[TimeOut]:
        return  self.time_repository.get_by_coo(coo_id)

    def get_times_by_gerente(self, gerente_id: int) -> List[TimeOut]:
        return self.time_repository.get_by_gerente(gerente_id)

    def get_times_by_user(self, user_id: int) -> List[TimeOut]:
        return  self.time_repository.list_by_user_id(user_id)
from src.application.repositories.ITimeRepository import ITimeRepository
from src.domain.entities.time_schema import TimeCreate, TimeUpdate
from src.infra.database.models import UserModel
from src.infra.database.models.time_model import TimeModel


class TimeRepository(ITimeRepository):
    def __init__(self, db_session):
        self.db = db_session

    def list_all(self):
        return self.db.query(TimeModel).all()

    def get_by_id(self, time_id: int):
        return self.db.query(TimeModel).filter_by(id=time_id).first()

    def create(self, data: TimeCreate):
        new_time = TimeModel(**data.model_dump())
        self.db.add(new_time)
        self.db.commit()
        self.db.refresh(new_time)
        self.db.close()
        return new_time

    def update(self, time_id: int, data: TimeUpdate):
        time = self.get_by_id(time_id)
        if not time:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(time, field, value)
        self.db.commit()
        self.db.refresh(time)
        self.db.close()
        return time

    def delete(self, time_id: int):
        time = self.get_by_id(time_id)
        if time:
            self.db.delete(time)
            self.db.commit()
            self.db.close()

    def get_by_coo(self, coo_id: int):
        return self.db.query(TimeModel).filter_by(coo_id=coo_id).all()

    def get_by_gerente(self, gerente_id: int):
        return self.db.query(TimeModel).filter_by(gerente_id=gerente_id).all()

    def get_by_name(self, name: str) -> TimeModel | None:
        return self.db.query(TimeModel).filter(TimeModel.name == name).first()

    def list_by_user_id(self, user_id: int) -> list[TimeModel]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return []
        return [db_user.time]

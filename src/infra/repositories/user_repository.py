from typing import Optional, List

from sqlalchemy.orm import Session

from src.application.repositories.iuser_repository import IUserRepository

from src.application.dtos.user_create_dto import UserCreateDTO
from src.infra.database.models.time_model import TimeModel
from src.infra.database.models.user_model import UserModel


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserCreateDTO):

        db_user = UserModel(
            username=user.username.strip(),
            full_name=user.full_name.strip(),
            cpf=user.cpf,
            role=user.role,
            hashed_password=user.hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        self.db.close()
        return db_user

    def update(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.db.close()
        return user

    def get_all(self):
        return self.db.query(UserModel).all()

    def get_by_username(self, username: str):
        try:
            return (
                self.db
                .query(UserModel)
                .filter(UserModel.username == username)
                .first()
            )
        finally:
            self.db.close()

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        try:
            return (
                self.db
                .query(UserModel)
                .filter(UserModel.id == user_id)
                .first()
            )
        finally:
            self.db.close()

    def get_by_cpf(self, cpf: str) -> Optional[UserModel]:
        try:
            return (
                self.db
                .query(UserModel)
                .filter(UserModel.cpf == cpf)
                .first()
                )
        finally:
            self.db.close()

    def get_by_role(self, role: str) -> List[UserModel]:
        try:
            return (
                self.db
                .query(UserModel)
                .filter(UserModel.role == role)
                .all()
            )
        finally:
            self.db.close()

    def get_gerentes_by_coo(self, coo_id: int) -> List[UserModel]:
        try:
            times = self.db.query(TimeModel).filter(TimeModel.coo_id == coo_id).all()
            gerente_ids = {t.gerente_id for t in times if t.gerente_id is not None}
            return (
                self.db
                .query(UserModel)
                .filter(UserModel.id.in_(gerente_ids))
                .all()
            )
        finally:
            self.db.close()

    def get_times_ids_by_gerente(self, gerente_id: int) -> List[int]:
        try:
            times = self.db.query(TimeModel).filter(TimeModel.gerente_id == gerente_id).all()
            return [t.id for t in times]
        finally:
            self.db.close()

    def get_colaboradores_by_gerente(self, gerente_id: int) -> List[UserModel]:
        try:
            times = self.db.query(TimeModel).filter(TimeModel.gerente_id == gerente_id).all()
            time_ids = [t.id for t in times]
            return (
                self.db.query(UserModel)
                .filter(UserModel.time_id.in_(time_ids))
                .all()
            )
        finally:
            self.db.close()     

    def get_colaboradores_by_time(self, time_id: int) -> List[UserModel]:
        try:
            return (
                self.db.query(UserModel)
                .filter(UserModel.time_id == time_id)
                .all()
            )
        finally:
            self.db.close() 
        
    def close(self):
        self.db.close()
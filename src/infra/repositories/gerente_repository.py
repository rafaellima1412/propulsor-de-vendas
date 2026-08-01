from sqlalchemy.orm import Session

from src.application.repositories.igerente_repository import IGerenteRepository
from src.domain.entities.user_schema import UserBase
from src.infra.database.models import UserModel


class GerenteRepository(IGerenteRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[UserModel]:
        return self.db.query(UserModel).all()

    def get_by_id(self, id: int) -> UserModel | None:
        return self.db.query(UserBase).filter(UserBase.id == id).first()

    def create(self, gerente: UserModel) -> UserModel:
        self.db.add(gerente)
        self.db.commit()
        self.db.refresh(gerente)
        return gerente

    def update(self, gerente: UserModel) -> UserModel:
        self.db.commit()
        self.db.refresh(gerente)
        return gerente

    def delete(self, id: int) -> None:
        gerente = self.get_by_id(id)
        if gerente:
            self.db.delete(gerente)
            self.db.commit()

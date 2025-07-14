from typing import List, Optional

from sqlalchemy.orm import Session

from src.application.repositories.igerente_repository import IGerenteRepository
from src.domain.entities.user_schema import UserBase, UserCreate


class GerenteRepository(IGerenteRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[UserBase]:
        return self.db.query(UserBase).all()

    def get_by_id(self, id: int) -> Optional[UserBase]:
        return self.db.query(UserBase).filter(UserBase.id == id).first()

    def create(self, gerente: UserCreate) -> UserCreate:
        self.db.add(gerente)
        self.db.commit()
        self.db.refresh(gerente)
        return gerente

    def update(self, gerente: UserBase) -> UserBase:
        self.db.commit()
        self.db.refresh(gerente)
        return gerente

    def delete(self, id: int) -> None:
        gerente = self.get_by_id(id)
        if gerente:
            self.db.delete(gerente)
            self.db.commit()
from typing import List

from sqlalchemy.orm import Session
from src.infra.database.models.venda_model import VendaModel
from src.application.dtos.venda_create_dto import VendaCreateDTO

class VendaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, venda: VendaCreateDTO):
        db_venda = VendaModel(**venda.model_dump())
        self.db.add(db_venda)
        self.db.commit()
        self.db.refresh(db_venda)
        return db_venda

    def get_all(self):
        return self.db.query(VendaModel).all()

    def get_by_id(self, venda_id: int):
        return self.db.query(VendaModel).filter(VendaModel.id == venda_id).first()

    def list_by_usuario_and_campanha(self, usuario_id: int, campanha_id: int) -> List[VendaModel]:
        return self.db.query(VendaModel).filter(
            VendaModel.campanha_id == campanha_id,
            VendaModel.usuario_id == usuario_id
        ).all()

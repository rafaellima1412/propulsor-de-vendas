from typing import List, Dict, Tuple

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from src.domain.enums.enums import PlanoInternet
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

    def contagem_por_plano(self, user_id: int) -> Dict[str, int]:
        resultados = (
            self.db.query(VendaModel.area, func.count(VendaModel.id))
            .filter(VendaModel.status == "vendido", VendaModel.usuario_id == user_id)
            .group_by(VendaModel.area)
            .all()
        )
        return {
            plano.value if isinstance(plano, PlanoInternet) else plano: count
            for plano, count in resultados
        }

    def contagem_por_mes(self, user_id: int) -> Dict[Tuple[int, int], int]:
        resultados = (
            self.db.query(
                extract('year', VendaModel.data_criacao).label("ano"),
                extract('month', VendaModel.data_criacao).label("mes"),
                func.count(VendaModel.id)
            )
            .filter(VendaModel.status == "vendido", VendaModel.usuario_id == user_id)
            .group_by("ano", "mes")
            .order_by("ano", "mes")
            .all()
        )
        return {(int(ano), int(mes)): count for ano, mes, count in resultados}

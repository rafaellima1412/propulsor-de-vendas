from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.domain.enums.enums import PlanoInternet
from src.infra.database.models.venda_model import VendaModel


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

    def contagem_por_plano(self, usuario_ids: int | list[int]) -> dict[str, int]:
        if isinstance(usuario_ids, int):
            usuario_ids = [usuario_ids]

        if not usuario_ids:
            return {}
        # print(usuario_ids, type(usuario_ids))
        resultados = (
            self.db.query(VendaModel.plano, func.count(VendaModel.id))
            .filter(
                VendaModel.status == "vendido",
                VendaModel.usuario_id.in_(usuario_ids),
            )
            .group_by(VendaModel.plano)
            .all()
        )

        return {
            plano.value if isinstance(plano, PlanoInternet) else plano: count
            for plano, count in resultados
        }

    def contagem_por_mes(self,usuario_ids: int | list[int]) -> dict[tuple[int, int], int]:
        if isinstance(usuario_ids, int):
            usuario_ids = [usuario_ids]

        if not usuario_ids:
            return {}

        resultados = (
            self.db.query(
                extract("year", VendaModel.data_criacao).label("ano"),
                extract("month", VendaModel.data_criacao).label("mes"),
                func.count(VendaModel.id),
            )
            .filter(
                VendaModel.status == "vendido",
                VendaModel.usuario_id.in_(usuario_ids),
            )
            .group_by("ano", "mes")
            .order_by("ano", "mes")
            .all()
        )

        return {
            (int(ano), int(mes)): count
            for ano, mes, count in resultados
        }

    def contagem_por_plano_all(self) -> dict[str, int]:
        """Igual a contagem_por_plano, mas sem filtro de usuário — todas as vendas da empresa."""
        resultados = (
            self.db.query(VendaModel.plano, func.count(VendaModel.id))
            .filter(VendaModel.status == "vendido")
            .group_by(VendaModel.plano)
            .all()
        )

        return {
            plano.value if isinstance(plano, PlanoInternet) else plano: count
            for plano, count in resultados
        }

    def contagem_por_mes_all(self) -> dict[tuple[int, int], int]:
        """Igual a contagem_por_mes, mas sem filtro de usuário — todas as vendas da empresa."""
        resultados = (
            self.db.query(
                extract("year", VendaModel.data_criacao).label("ano"),
                extract("month", VendaModel.data_criacao).label("mes"),
                func.count(VendaModel.id),
            )
            .filter(VendaModel.status == "vendido")
            .group_by("ano", "mes")
            .order_by("ano", "mes")
            .all()
        )

        return {
            (int(ano), int(mes)): count
            for ano, mes, count in resultados
        }
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.application.dtos.carteira_financeira_dto import CarteiraFinanceiraDTO
from src.infra.database.models import VendaModel


class CarteiraFinanceiraRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_carteira_by_usuario_id(self, usuario_id: int) -> CarteiraFinanceiraDTO:
        total_receitas = (
            self.session.query(func.sum(VendaModel.valor))
            .filter(VendaModel.usuario_id == usuario_id, VendaModel.status == "vendido")
            .scalar()
            or 0
        )
        # total_despesas = (
        #     self.session.query(func.sum(DespesaModel.valor))
        #     .filter(DespesaModel.usuario_id == usuario_id)
        #     .scalar() or 0
        # )
        total_despesas = 1
        saldo_atual = total_receitas - total_despesas

        return CarteiraFinanceiraDTO(
            usuario_id=usuario_id,
            saldo_atual=saldo_atual,
            total_receitas=total_receitas,
            total_despesas=total_despesas,
        )

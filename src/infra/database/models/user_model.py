from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.infra.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    full_name = Column(String)
    role = Column(String)
    cpf = Column(String(14), unique=True)
    hashed_password = Column(String)

    is_active = Column(Boolean, nullable=False, default=True)
    descricao = Column(String)

    time_id = Column(Integer, ForeignKey("times.id"), nullable=True)

    campanhas = relationship(
        "CampanhaModel",
        secondary="user_campanha",
        back_populates="usuarios"
    )

    vendas = relationship(
        "VendaModel",
        back_populates="usuario"
    )
    # para reverse relations:
    times_gerenciados = relationship(
        "TimeModel",
        back_populates="gerente",
        foreign_keys="TimeModel.gerente_id"
    )
    # para reverse relations:
    times_coordenados = relationship(
        "TimeModel",
        back_populates="coo",
        foreign_keys="TimeModel.coo_id"
    )

    time = relationship(
        "TimeModel",
        back_populates="colaboradores",
        foreign_keys=[time_id],
        lazy="joined"
    )

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.database.base import Base
from src.infra.database.models.user_model import UserModel
from src.infra.database.models.campanha_time import campanha_time

if TYPE_CHECKING:
    from src.infra.database.models.local_model import Local


class TimeModel(Base):
    __tablename__ = "times"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))

    local_id: Mapped[int] = mapped_column(ForeignKey("locais.id"), nullable=True)

    local: Mapped["Local"] = relationship("Local", back_populates="times")

    gerente_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    gerente = relationship("UserModel", foreign_keys=[gerente_id], back_populates="times_gerenciados", lazy="joined")

    coo_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    coo = relationship("UserModel", foreign_keys=[coo_id], back_populates="times_coordenados", lazy="joined")

    # Esse relacionamento deve apontar explicitamente a FK usada: UserModel.time_id
    colaboradores = relationship("UserModel", back_populates="time", foreign_keys=[UserModel.time_id])
    campanhas = relationship("CampanhaModel", secondary=campanha_time, back_populates="times")

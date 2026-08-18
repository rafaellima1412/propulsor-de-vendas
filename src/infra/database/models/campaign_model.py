from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.infra.database.base import Base


class CampanhaModel(Base):
    __tablename__ = "campanhas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # tem
    paragraph = Column(String, nullable=False)  # tem
    image = Column(String, nullable=False)  # tem
    post_type = Column(String, nullable=True)
    url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    folder_url = Column(String, nullable=True)
    qrcode_url = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=datetime.now(UTC))

    # A campanha É o time/região: o coordenador responsável fica direto
    # aqui, sem uma tabela "times" separada no meio.
    coordenador_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    coordenador = relationship("UserModel", foreign_keys=[coordenador_id], lazy="joined")

    usuarios = relationship("UserModel", secondary="user_campanha", back_populates="campanhas")
    vendas = relationship("VendaModel", back_populates="campanha", cascade="all, delete-orphan")

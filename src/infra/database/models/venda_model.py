
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Enum, ForeignKey,DateTime
from sqlalchemy.orm import relationship
from src.domain.enums.enums import PlanoInternet, StatusVenda
from src.infra.database.base import Base


class VendaModel(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)

    plano = Column(Enum(PlanoInternet), nullable=False)
    status = Column(Enum(StatusVenda), nullable=False)

    descricao = Column(String, nullable=True)

    cpf_vendedor = Column(String(14), nullable=False)

    data_criacao = Column(DateTime, default=datetime.now(timezone.utc))

    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campanha_id = Column(Integer, ForeignKey("campanhas.id"), nullable=False)

    usuario = relationship("UserModel", back_populates="vendas")
    campanha = relationship("CampanhaModel", back_populates="vendas")

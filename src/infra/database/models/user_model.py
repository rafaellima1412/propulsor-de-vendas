from sqlalchemy import Boolean, Column, Integer, String
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

    campanhas = relationship("CampanhaModel", secondary="user_campanha", back_populates="usuarios")

    vendas = relationship("VendaModel", back_populates="usuario")

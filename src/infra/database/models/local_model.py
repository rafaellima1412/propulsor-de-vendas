from geoalchemy2 import Geography
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.infra.database.base import Base


class Local(Base):
    __tablename__ = "locais"

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    coordenadas = Column(Geography(geometry_type="POINT", srid=4326))

    times = relationship("TimeModel", back_populates="local")

from sqlalchemy import Column, ForeignKey, Integer, Table

from src.infra.database.base import Base

campanha_time = Table(
    "campanha_time",
    Base.metadata,
    Column("campanha_id", Integer, ForeignKey("campanhas.id"), primary_key=True),
    Column("time_id", Integer, ForeignKey("times.id"), primary_key=True),
)

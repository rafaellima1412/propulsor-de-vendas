from sqlalchemy import Column, ForeignKey, Integer, Table

from src.infra.database.base import Base

user_campanha = Table(
    "user_campanha",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("campanha_id", Integer, ForeignKey("campanhas.id"), primary_key=True),
)

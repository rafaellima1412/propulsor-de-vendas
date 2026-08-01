from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infra.settings.settings import settings

DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)

from sqlalchemy.orm import Session

from src.infra.database.session import SessionLocal


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

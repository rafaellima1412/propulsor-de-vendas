import os

os.environ["POSTGRES_DB"] = os.environ.get("TEST_POSTGRES_DB", "propulsor_vendas_test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from main import app  # noqa: E402
from src.infra.database.base import Base  # noqa: E402
from src.infra.database.session import engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _schema():
    """Create all tables once for the whole test session."""
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def _clean_tables():
    print(">>> limpando banco")

    engine.dispose()

    with engine.begin() as conn:
        table_names = [t.name for t in Base.metadata.tables.values()]
        if table_names:
            quoted = ", ".join(f'"{name}"' for name in table_names)
            conn.execute(
                text(
                    f"TRUNCATE {quoted} RESTART IDENTITY CASCADE;"
                )
            )

    print(">>> banco limpo")

    yield

    engine.dispose()


@pytest.fixture
def client():
    yield TestClient(app)
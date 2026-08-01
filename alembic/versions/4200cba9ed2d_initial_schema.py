"""initial schema

Revision ID: 4200cba9ed2d
Revises:
Create Date: 2025-08-11 11:43:06.274159
"""

from collections.abc import Sequence

import sqlalchemy as sa
from geoalchemy2 import Geography

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4200cba9ed2d"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # cria a extensão postgis (se ainda não existir)
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    # cria tabela locais
    op.create_table(
        "locais",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.String(length=100), nullable=True),
        sa.Column("coordenadas", Geography(geometry_type="POINT", srid=4326), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("locais")
    op.execute("DROP EXTENSION IF EXISTS postgis CASCADE")

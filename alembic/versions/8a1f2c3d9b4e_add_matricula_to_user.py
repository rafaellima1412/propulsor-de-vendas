"""add matricula to users

Revision ID: 8a1f2c3d9b4e
Revises: 4200cba9ed2d
Create Date: 2026-08-05 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a1f2c3d9b4e"
down_revision: str | Sequence[str] | None = "4200cba9ed2d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("matricula", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "matricula")
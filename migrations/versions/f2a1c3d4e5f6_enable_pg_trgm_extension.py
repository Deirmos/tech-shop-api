"""Enable pg_trgm extension

Revision ID: f2a1c3d4e5f6
Revises: b683cbbf3d4d
Create Date: 2026-03-17 17:29:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f2a1c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "b683cbbf3d4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")

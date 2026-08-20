"""add_skill_pack_badges

Revision ID: b3c4d5e6f709
Revises: a1b2c3d4e5f8
Create Date: 2026-08-20 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "b3c4d5e6f709"
down_revision: str | None = "a1b2c3d4e5f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "skill_packs",
        sa.Column("badges", JSONB, nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("skill_packs", "badges")

"""exp06 key unique among LIVE experiments only (ADR-017 §18 round 3)

A surface key must be reusable after its experiment reaches a terminal
status — the global unique made every well-known surface one-shot forever.

Revision ID: exp06a00006
Revises: exp05a00005
Create Date: 2026-09-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "exp06a00006"
down_revision: str | None = "exp05a00005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("experiments_key_key", "experiments", type_="unique")
    op.create_index(
        "uq_experiments_live_key",
        "experiments",
        ["key"],
        unique=True,
        postgresql_where=sa.text("status NOT IN ('promoted', 'rejected', 'archived')"),
    )
    op.create_index("ix_experiments_key", "experiments", ["key"])


def downgrade() -> None:
    op.drop_index("ix_experiments_key", table_name="experiments")
    op.drop_index("uq_experiments_live_key", table_name="experiments")
    op.create_unique_constraint("experiments_key_key", "experiments", ["key"])

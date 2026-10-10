"""exp09 holdout key unique among ACTIVE groups only (ADR-017 §18)

A released group must not hold its key hostage — same lesson as the exp06
live-only experiment key (round 3).

Revision ID: exp09a00009
Revises: exp08a00008
Create Date: 2026-10-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "exp09a00009"
down_revision: str | None = "exp08a00008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "experiment_holdout_groups"


def upgrade() -> None:
    op.drop_constraint(f"{_TABLE}_key_key", _TABLE, type_="unique")
    op.create_index(
        "uq_experiment_holdout_groups_active_key",
        _TABLE,
        ["key"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index("uq_experiment_holdout_groups_active_key", table_name=_TABLE)
    op.create_unique_constraint(f"{_TABLE}_key_key", _TABLE, ["key"])

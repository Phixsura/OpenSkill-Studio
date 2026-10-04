"""exp08 snapshot segment dimension (ADR-017 §4.8 v2)

Revision ID: exp08a00008
Revises: exp07a00007
Create Date: 2026-10-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "exp08a00008"
down_revision: str | None = "exp07a00007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UQ = "uq_experiment_metric_snapshots_window"
_TABLE = "experiment_metric_snapshots"


def upgrade() -> None:
    op.add_column(
        _TABLE,
        sa.Column("segment", sa.String(length=64), server_default="", nullable=False),
    )
    op.drop_constraint(_UQ, _TABLE, type_="unique")
    op.create_unique_constraint(
        _UQ,
        _TABLE,
        ["experiment_id", "metric_key", "segment", "variant_key", "window_start"],
    )


def downgrade() -> None:
    op.drop_constraint(_UQ, _TABLE, type_="unique")
    op.create_unique_constraint(
        _UQ, _TABLE, ["experiment_id", "metric_key", "variant_key", "window_start"]
    )
    op.drop_column(_TABLE, "segment")

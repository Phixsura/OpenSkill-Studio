"""Control plane: exact (unrounded) billable/cost columns on cp_rated_usage

R75: rating quantized billable/internal cost to integer minor units PER EVENT,
so any event whose marginal charge was < 0.5 minor rounded to 0 — unbounded
under-billing (a $1/1M-token policy billed 0 for every sub-500k-token event).
Add Numeric(24,8) exact columns; charging/budget/settlement now sum the exact
column and round ONCE (round-of-sum). Backfill existing rows from the rounded
integers (best available history; new ratings carry true precision).

Revision ID: cp12f0000012
Revises: cp11e0000011
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cp12f0000012"
down_revision: str | None = "cp11e0000011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cp_rated_usage",
        sa.Column(
            "billable_amount_exact",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "cp_rated_usage",
        sa.Column(
            "internal_cost_exact",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )
    # Backfill: existing rows only have the rounded integers — seed the exact
    # columns from them so historical sums stay consistent.
    op.execute(
        "UPDATE cp_rated_usage SET billable_amount_exact = billable_amount_minor, "
        "internal_cost_exact = internal_cost_minor"
    )


def downgrade() -> None:
    op.drop_column("cp_rated_usage", "internal_cost_exact")
    op.drop_column("cp_rated_usage", "billable_amount_exact")

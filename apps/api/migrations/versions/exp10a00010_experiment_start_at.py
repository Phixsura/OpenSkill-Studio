"""exp10 scheduled auto-start (ADR-017 §18 round 60)

'scheduled' used to mean launch-checked-awaiting-a-human: without a start
time and a sweep, the status name over-promised. start_at is optional —
NULL keeps the manual-start behavior.

Revision ID: exp10a00010
Revises: exp09a00009
Create Date: 2026-10-02

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "exp10a00010"
down_revision: str | None = "exp09a00009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "experiments",
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
    )
    # the start sweep scans scheduled experiments by their due time
    op.create_index(
        "ix_experiments_scheduled_start",
        "experiments",
        ["status", "start_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_experiments_scheduled_start", table_name="experiments")
    op.drop_column("experiments", "start_at")

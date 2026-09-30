"""eco04 watchlist noise controls: min_severity + muted_until (ADR-016 §24).

Revision ID: eco04a00004
Revises: eco03a00003
Create Date: 2026-09-22
"""

import sqlalchemy as sa
from alembic import op

revision: str = "eco04a00004"
down_revision: str = "eco03a00003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "eco_watchlists",
        sa.Column("min_severity", sa.String(30), nullable=False, server_default="info"),
    )
    op.add_column(
        "eco_watchlists",
        sa.Column("muted_until", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("eco_watchlists", "muted_until")
    op.drop_column("eco_watchlists", "min_severity")

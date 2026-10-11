"""Delivery payload archive (ADR-018 §12, R94 — byte-exact wire proof)

Revision ID: intg13a00013
Revises: intg12a00012
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op

revision = "intg13a00013"
down_revision = "intg12a00012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_event_deliveries",
        sa.Column("request_body", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("intg_event_deliveries", "request_body")

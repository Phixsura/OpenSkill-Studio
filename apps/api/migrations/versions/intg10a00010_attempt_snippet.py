"""Response snippet on delivery attempts (ADR-018 §12, R60 — Svix parity)

Revision ID: intg10a00010
Revises: intg09a00009
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op

revision = "intg10a00010"
down_revision = "intg09a00009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_delivery_attempts",
        sa.Column("response_snippet", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("intg_delivery_attempts", "response_snippet")

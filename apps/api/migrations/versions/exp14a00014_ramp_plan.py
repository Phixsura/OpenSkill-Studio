"""scheduled ramp plans (ADR-017 round 129)

Revision ID: exp14a00014
Revises: exp13a00013
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "exp14a00014"
down_revision = "exp13a00013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "experiments", sa.Column("ramp_plan", JSONB(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("experiments", "ramp_plan")

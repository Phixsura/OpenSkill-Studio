"""quantile metrics (ADR-017 section 4.14): snapshot value_histogram

Revision ID: exp13a00013
Revises: exp12a00012
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "exp13a00013"
down_revision = "exp12a00012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "experiment_metric_snapshots",
        sa.Column(
            "value_histogram",
            JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("experiment_metric_snapshots", "value_histogram")

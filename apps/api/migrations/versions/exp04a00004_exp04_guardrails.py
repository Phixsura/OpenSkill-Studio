"""exp04 guardrail events + sweep-fairness stamp (ADR-017 §4.8, §9)

Revision ID: exp04a00004
Revises: exp03a00003
Create Date: 2026-09-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "exp04a00004"
down_revision: str | None = "exp03a00003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiment_guardrail_events",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column("guardrail_key", sa.String(length=64), nullable=False),
        sa.Column("metric_key", sa.String(length=64), nullable=True),
        sa.Column("observed", sa.Numeric(24, 6), nullable=True),
        sa.Column("threshold", sa.Numeric(24, 6), nullable=True),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("action", sa.String(length=10), nullable=False),
        sa.Column("auto", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "detail", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_experiment_guardrail_events_exp_created",
        "experiment_guardrail_events",
        ["experiment_id", "created_at"],
    )
    op.add_column(
        "experiments",
        sa.Column("last_guardrail_check_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("experiments", "last_guardrail_check_at")
    op.drop_table("experiment_guardrail_events")

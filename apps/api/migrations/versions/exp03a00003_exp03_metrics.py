"""exp03 metric definitions & snapshots (ADR-017 §4.6-§4.7)

Revision ID: exp03a00003
Revises: exp02a00002
Create Date: 2026-09-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "exp03a00003"
down_revision: str | None = "exp02a00002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiment_metric_definitions",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("domain", sa.String(length=20), nullable=False),
        sa.Column("source_kind", sa.String(length=10), nullable=False),
        sa.Column("query_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "spec", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False
        ),
        sa.Column(
            "privacy_class", sa.String(length=16), server_default="aggregate_only", nullable=False
        ),
        sa.Column(
            "direction", sa.String(length=16), server_default="increase_good", nullable=False
        ),
        sa.Column("winsorize_pct", sa.Numeric(6, 3), nullable=True),
        sa.Column("cap_value", sa.Numeric(24, 6), nullable=True),
        sa.Column("percentile", sa.Numeric(6, 3), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )

    op.create_table(
        "experiment_metric_snapshots",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column("metric_key", sa.String(length=64), nullable=False),
        sa.Column("variant_key", sa.String(length=40), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("n", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("numerator", sa.Numeric(24, 6), nullable=True),
        sa.Column("denominator", sa.Numeric(24, 6), nullable=True),
        sa.Column("sum_value", sa.Numeric(24, 6), nullable=True),
        sa.Column("sum_sq", sa.Numeric(30, 6), nullable=True),
        sa.Column("cov_sum", sa.Numeric(24, 6), nullable=True),
        sa.Column("cov_sum_sq", sa.Numeric(30, 6), nullable=True),
        sa.Column("cov_xy_sum", sa.Numeric(30, 6), nullable=True),
        sa.Column(
            "provenance",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "experiment_id",
            "metric_key",
            "variant_key",
            "window_start",
            name="uq_experiment_metric_snapshots_window",
        ),
    )
    op.create_index(
        "ix_experiment_metric_snapshots_exp_metric",
        "experiment_metric_snapshots",
        ["experiment_id", "metric_key"],
    )


def downgrade() -> None:
    op.drop_table("experiment_metric_snapshots")
    op.drop_table("experiment_metric_definitions")

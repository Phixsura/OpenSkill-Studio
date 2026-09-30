"""exp02 assignments & exposures (ADR-017 §4.4-§4.5)

Revision ID: exp02a00002
Revises: exp01a00001
Create Date: 2026-09-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "exp02a00002"
down_revision: str | None = "exp01a00001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiment_assignments",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column("unit_type", sa.String(length=24), nullable=False),
        sa.Column("unit_id", sa.String(length=26), nullable=False),
        sa.Column("variant_key", sa.String(length=40), nullable=False),
        sa.Column("assigned_version", sa.Integer(), nullable=False),
        sa.Column("bucket", sa.Integer(), nullable=False),
        sa.Column("is_holdout", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "experiment_id", "unit_type", "unit_id", name="uq_experiment_assignments_unit"
        ),
    )
    op.create_index(
        "ix_experiment_assignments_unit", "experiment_assignments", ["unit_type", "unit_id"]
    )
    op.create_index(
        "ix_experiment_assignments_exp_variant",
        "experiment_assignments",
        ["experiment_id", "variant_key"],
    )

    op.create_table(
        "experiment_exposures",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("assignment_id", sa.String(length=26), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "context", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False
        ),
        sa.Column("dedup_key", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["assignment_id"], ["experiment_assignments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_experiment_exposures_exp_occurred",
        "experiment_exposures",
        ["experiment_id", "occurred_at"],
    )
    op.create_index(
        "uq_experiment_exposures_dedup",
        "experiment_exposures",
        ["experiment_id", "dedup_key"],
        unique=True,
        postgresql_where=sa.text("dedup_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_table("experiment_exposures")
    op.drop_table("experiment_assignments")

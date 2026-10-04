"""exp01 experiment core models (ADR-017 §4.1-§4.3, §4.11)

Revision ID: exp01a00001
Revises: eco10a00010
Create Date: 2026-09-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "exp01a00001"
down_revision: str | None = "eco10a00010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiment_layers",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("domain", sa.String(length=20), nullable=False),
        sa.Column("total_slices", sa.Integer(), server_default="10000", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )

    op.create_table(
        "experiments",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("domain", sa.String(length=20), nullable=False),
        sa.Column("scope_org_id", sa.String(length=26), nullable=True),
        sa.Column("layer_key", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=12), server_default="draft", nullable=False),
        sa.Column("current_version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("owner_user_id", sa.String(length=26), nullable=False),
        sa.Column("risk_class", sa.String(length=8), server_default="medium", nullable=False),
        sa.Column("ramp_bp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("holdout_bp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("analysis_close_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["scope_org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["layer_key"], ["experiment_layers.key"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_experiments_status_domain", "experiments", ["status", "domain"])
    op.create_index("ix_experiments_layer", "experiments", ["layer_key"])
    op.create_index("ix_experiments_scope_org", "experiments", ["scope_org_id"])

    op.create_table(
        "experiment_versions",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "spec", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False
        ),
        sa.Column("spec_hash", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.String(length=26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("experiment_id", "version", name="uq_experiment_versions_exp_version"),
    )

    op.create_table(
        "experiment_layer_allocations",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("layer_key", sa.String(length=64), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column("slice_start", sa.Integer(), nullable=False),
        sa.Column("slice_end", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["layer_key"], ["experiment_layers.key"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("experiment_id", name="uq_experiment_layer_allocations_experiment"),
    )
    op.create_index(
        "ix_experiment_layer_allocations_layer", "experiment_layer_allocations", ["layer_key"]
    )

    op.create_table(
        "experiment_events",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column("actor_user_id", sa.String(length=26), nullable=True),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column(
            "payload", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_experiment_events_exp_created", "experiment_events", ["experiment_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_table("experiment_events")
    op.drop_table("experiment_layer_allocations")
    op.drop_table("experiment_versions")
    op.drop_index("ix_experiments_scope_org", table_name="experiments")
    op.drop_index("ix_experiments_layer", table_name="experiments")
    op.drop_index("ix_experiments_status_domain", table_name="experiments")
    op.drop_table("experiments")
    op.drop_table("experiment_layers")

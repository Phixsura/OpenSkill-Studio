"""Control plane: append-only usage events (Issue #27, ADR-014 §3).

Revision ID: cp03c0000003
Revises: cp02b0000002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "cp03c0000003"
down_revision: str | None = "cp02b0000002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_usage_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("user_id", sa.String(26), nullable=True),
        sa.Column("project_id", sa.String(26), nullable=True),
        sa.Column("workflow_run_id", sa.String(26), nullable=True),
        sa.Column("evaluation_task_id", sa.String(26), nullable=True),
        sa.Column("provider_connection_id", sa.String(26), nullable=True),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("model_or_service", sa.String(200), nullable=True),
        sa.Column("usage_type", sa.String(40), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(120), nullable=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("adjustment_of_id", sa.String(26), nullable=True),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_usage_idem",
        "cp_usage_events",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.create_index("ix_cp_usage_tenant_time", "cp_usage_events", ["tenant_id", "occurred_at"])
    op.create_index("ix_cp_usage_org_time", "cp_usage_events", ["org_id", "occurred_at"])
    op.create_index("ix_cp_usage_type_time", "cp_usage_events", ["usage_type", "occurred_at"])


def downgrade() -> None:
    op.drop_table("cp_usage_events")

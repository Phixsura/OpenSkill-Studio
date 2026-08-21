"""add missing columns and gamification tables

Revision ID: d5e6f70b1120
Revises: c4d5e6f70a10
Create Date: 2026-08-21 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "d5e6f70b1120"
down_revision: str | None = "c4d5e6f70a10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- missing columns ---
    op.add_column("skill_packs", sa.Column("quality_score", sa.Integer(), nullable=True))
    op.add_column("skill_packs", sa.Column("sharing_enabled", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("skills", sa.Column("sandbox_url", sa.String(500), nullable=True))
    op.add_column("exercises", sa.Column("sandbox_config", JSONB(), nullable=True))
    op.add_column("learning_path_items", sa.Column("drip_schedule", JSONB(), nullable=True))

    # --- gamification tables ---
    op.create_table(
        "user_points",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_user_points_user_org", "user_points", ["user_id", "org_id"], unique=True)
    op.create_index("ix_user_points_org_total", "user_points", ["org_id", "total_points"])

    op.create_table(
        "points_ledger",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("reference_id", sa.String(26), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_points_ledger_user_org", "points_ledger", ["user_id", "org_id"])

    # --- webhook subscriptions table ---
    op.create_table(
        "webhook_subscriptions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("events", JSONB(), nullable=False, server_default="[]"),
        sa.Column("secret", sa.String(64), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_webhooks_org_active", "webhook_subscriptions", ["org_id", "active"])


def downgrade() -> None:
    op.drop_index("ix_webhooks_org_active", table_name="webhook_subscriptions")
    op.drop_table("webhook_subscriptions")
    op.drop_index("ix_points_ledger_user_org", table_name="points_ledger")
    op.drop_table("points_ledger")
    op.drop_index("ix_user_points_org_total", table_name="user_points")
    op.drop_index("uq_user_points_user_org", table_name="user_points")
    op.drop_table("user_points")
    op.drop_column("learning_path_items", "drip_schedule")
    op.drop_column("exercises", "sandbox_config")
    op.drop_column("skills", "sandbox_url")
    op.drop_column("skill_packs", "sharing_enabled")
    op.drop_column("skill_packs", "quality_score")

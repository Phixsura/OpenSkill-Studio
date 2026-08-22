"""Notification preferences, approval audit trail

Revision ID: a1b2c3d4e5f8
Revises: b2c3d4e5f607
Create Date: 2026-08-20 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f8"
down_revision: str | None = "b2c3d4e5f607"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── user_notification_preferences ──
    op.create_table(
        "user_notification_preferences",
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("preferences", JSONB, nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── pack_approval_events ──
    op.create_table(
        "pack_approval_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("pack_id", sa.String(26), sa.ForeignKey("skill_packs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("actor_id", sa.String(26), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_pack_approval_events_pack", "pack_approval_events", ["pack_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_pack_approval_events_pack", table_name="pack_approval_events")
    op.drop_table("pack_approval_events")
    op.drop_table("user_notification_preferences")

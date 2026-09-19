"""talent06: notifications, endorsements, activity log

Revision ID: talent06a00006
Revises: talent05a00005
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "talent06a00006"
down_revision = "talent05a00005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- Notification preferences --
    op.create_table(
        "talent_notification_preferences",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(20), nullable=False, server_default="in_app"),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_notif_pref_user", "talent_notification_preferences", ["user_id"])
    op.create_index(
        "ix_notif_pref_user_event",
        "talent_notification_preferences",
        ["user_id", "event_type"],
        unique=True,
    )

    # -- Notifications --
    op.create_table(
        "talent_notifications",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("metadata", JSONB, server_default="{}", nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_notif_user_created",
        "talent_notifications",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_notif_user_read",
        "talent_notifications",
        ["user_id", "read_at"],
    )
    op.create_index("ix_notif_event_type", "talent_notifications", ["event_type"])

    # -- Skill endorsements --
    op.create_table(
        "talent_skill_endorsements",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "endorser_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "capability_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("relationship", sa.String(30), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="accepted"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_endorse_user", "talent_skill_endorsements", ["user_id"])
    op.create_index("ix_endorse_endorser", "talent_skill_endorsements", ["endorser_id"])
    op.create_index("ix_endorse_cap", "talent_skill_endorsements", ["capability_id"])
    op.create_index(
        "ix_endorse_unique",
        "talent_skill_endorsements",
        ["user_id", "endorser_id", "capability_id"],
        unique=True,
    )

    # -- Activity log --
    op.create_table(
        "talent_activity_log",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("metadata", JSONB, server_default="{}", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_activity_user_created",
        "talent_activity_log",
        ["user_id", "created_at"],
    )
    op.create_index("ix_activity_action", "talent_activity_log", ["action_type"])
    op.create_index(
        "ix_activity_target",
        "talent_activity_log",
        ["target_type", "target_id"],
    )


def downgrade() -> None:
    op.drop_table("talent_activity_log")
    op.drop_table("talent_skill_endorsements")
    op.drop_table("talent_notifications")
    op.drop_table("talent_notification_preferences")

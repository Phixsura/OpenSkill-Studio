"""Event mesh: canonical events, deliveries, attempts; webhook secret rotation
columns (ADR-018 §12, P2)

Revision ID: intg02a00002
Revises: intg01a00001
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg02a00002"
down_revision = "intg01a00001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("source", sa.String(200), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("dataschema", sa.String(200), nullable=True),
        sa.Column("data", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_intg_events_org_type_time", "intg_events", ["org_id", "type", "time"])

    op.create_table(
        "intg_event_deliveries",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "event_id",
            sa.String(26),
            sa.ForeignKey("intg_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "subscription_id",
            sa.String(26),
            sa.ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempt_count", sa.Integer, nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replay_of", sa.String(26), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_delivery_event_sub",
        "intg_event_deliveries",
        ["event_id", "subscription_id"],
        unique=True,
        postgresql_where=sa.text("replay_of IS NULL"),
    )
    op.create_index(
        "ix_intg_delivery_sub_status",
        "intg_event_deliveries",
        ["subscription_id", "status", "created_at"],
    )

    op.create_table(
        "intg_delivery_attempts",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "delivery_id",
            sa.String(26),
            sa.ForeignKey("intg_event_deliveries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("error", sa.String(200), nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_intg_attempts_delivery", "intg_delivery_attempts", ["delivery_id", "attempted_at"]
    )

    # Zero-downtime secret rotation (§12.2): previous secret keeps signing
    # for 7 days after rotation.
    op.add_column("webhook_subscriptions", sa.Column("secret_prev", sa.String(64), nullable=True))
    op.add_column(
        "webhook_subscriptions",
        sa.Column("secret_rotated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("webhook_subscriptions", "secret_rotated_at")
    op.drop_column("webhook_subscriptions", "secret_prev")
    op.drop_index("ix_intg_attempts_delivery", table_name="intg_delivery_attempts")
    op.drop_table("intg_delivery_attempts")
    op.drop_index("ix_intg_delivery_sub_status", table_name="intg_event_deliveries")
    op.drop_index("uq_intg_delivery_event_sub", table_name="intg_event_deliveries")
    op.drop_table("intg_event_deliveries")
    op.drop_index("ix_intg_events_org_type_time", table_name="intg_events")
    op.drop_table("intg_events")

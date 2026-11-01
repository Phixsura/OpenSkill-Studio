"""Developer Platform — webhook delivery log table.

Revision ID: devplatform02
Revises: devplatform01
Create Date: 2026-10-22
"""

from alembic import op
import sqlalchemy as sa

revision = "devplatform02"
down_revision = "devplatform01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_webhook_deliveries",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("app_id", sa.String(26), sa.ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installation_id", sa.String(26), sa.ForeignKey("app_installations.id", ondelete="SET NULL")),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_id", sa.String(64), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "DELIVERED", "FAILED", "RETRYING", name="webhook_delivery_status", create_constraint=True), default="PENDING"),
        sa.Column("http_status", sa.Integer),
        sa.Column("attempt", sa.Integer, default=1),
        sa.Column("max_attempts", sa.Integer, default=3),
        sa.Column("error_message", sa.Text),
        sa.Column("duration_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_app_wh_delivery_app", "app_webhook_deliveries", ["app_id", "created_at"])
    op.create_index("ix_app_wh_delivery_install", "app_webhook_deliveries", ["installation_id"])
    op.create_index("ix_app_wh_delivery_status", "app_webhook_deliveries", ["status"])


def downgrade() -> None:
    op.drop_table("app_webhook_deliveries")
    sa.Enum(name="webhook_delivery_status").drop(op.get_bind(), checkfirst=True)

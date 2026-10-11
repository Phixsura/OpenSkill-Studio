"""Delivery retention index (ADR-018 §12, R163 — nightly sweep scans status+time)

Revision ID: intg15a00015
Revises: intg14a00014
Create Date: 2026-10-11
"""

from alembic import op

revision = "intg15a00015"
down_revision = "intg14a00014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The nightly retention sweep deletes terminal deliveries by
    # (status IN (...), created_at < cutoff) across ALL subscriptions — the
    # existing (subscription_id, status, created_at) index can't serve it
    # (wrong leading column), so it full-scans. This index does.
    op.create_index(
        "ix_intg_delivery_status_created",
        "intg_event_deliveries",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_intg_delivery_status_created", table_name="intg_event_deliveries")

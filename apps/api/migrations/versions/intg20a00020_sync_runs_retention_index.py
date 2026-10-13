"""R393: partial index for the sync-run retention sweep. The nightly delete
(status terminal AND created_at < cutoff) seq-scanned intg_sync_runs once it
passed ~10k rows — caught live by the EXPLAIN drill the same day the storms
pushed the dev table over the threshold.

Revision ID: intg20a00020
Revises: intg19a00019
Create Date: 2026-10-13
"""

from alembic import op

revision = "intg20a00020"
down_revision = "intg19a00019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_intg_runs_retention",
        "intg_sync_runs",
        ["created_at"],
        postgresql_where="status IN ('succeeded','failed','cancelled')",
    )


def downgrade() -> None:
    op.drop_index("ix_intg_runs_retention", table_name="intg_sync_runs")

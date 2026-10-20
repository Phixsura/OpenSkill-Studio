"""R545: partial indexes for the scheduled-sweep scans.

The hourly/daily sweeps select `enabled AND schedule IN (...)` across ALL
orgs — flagged as a 34k-row Seq Scan by the EXPLAIN drill once the dev DB
grew. Partial indexes keep the fleet-wide sweeps index-driven.

Revision ID: intg25a00025
Revises: intg24a00024
"""

import sqlalchemy as sa
from alembic import op

revision = "intg25a00025"
down_revision = "intg24a00024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_intg_export_sweep",
        "intg_export_streams",
        ["schedule"],
        postgresql_where=sa.text("enabled"),
    )
    op.create_index(
        "ix_intg_syncprof_sweep",
        "intg_sync_profiles",
        ["schedule"],
        postgresql_where=sa.text("enabled"),
    )


def downgrade() -> None:
    op.drop_index("ix_intg_syncprof_sweep", table_name="intg_sync_profiles")
    op.drop_index("ix_intg_export_sweep", table_name="intg_export_streams")

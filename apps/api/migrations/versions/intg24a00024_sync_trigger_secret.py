"""R497: inbound sync-trigger webhook secret (CDC-lite change notification).

Revision ID: intg24a00024
Revises: intg23a00023
"""

import sqlalchemy as sa
from alembic import op

revision = "intg24a00024"
down_revision = "intg23a00023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_sync_profiles",
        sa.Column("trigger_secret_hash", sa.String(64), nullable=True),
    )
    op.create_unique_constraint(
        "uq_intg_syncprof_trigger_secret", "intg_sync_profiles", ["trigger_secret_hash"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_intg_syncprof_trigger_secret", "intg_sync_profiles", type_="unique")
    op.drop_column("intg_sync_profiles", "trigger_secret_hash")

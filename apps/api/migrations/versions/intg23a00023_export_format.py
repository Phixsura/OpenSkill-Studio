"""R486: export stream part format (ndjson | parquet).

Revision ID: intg23a00023
Revises: intg22a00022
"""

import sqlalchemy as sa
from alembic import op

revision = "intg23a00023"
down_revision = "intg22a00022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_export_streams",
        sa.Column("format", sa.String(10), nullable=False, server_default="ndjson"),
    )


def downgrade() -> None:
    op.drop_column("intg_export_streams", "format")

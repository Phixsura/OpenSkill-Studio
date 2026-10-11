"""Header-alias map on import jobs (ADR-018 §14, R92)

Revision ID: intg12a00012
Revises: intg11a00011
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg12a00012"
down_revision = "intg11a00011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_import_jobs",
        sa.Column("header_map", JSONB, nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("intg_import_jobs", "header_map")

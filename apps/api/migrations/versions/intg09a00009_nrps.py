"""LTI NRPS membership URL on resource links (ADR-018 §8, R49)

Revision ID: intg09a00009
Revises: intg08a00008
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op

revision = "intg09a00009"
down_revision = "intg08a00008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_lti_resource_links",
        sa.Column("nrps_url", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("intg_lti_resource_links", "nrps_url")

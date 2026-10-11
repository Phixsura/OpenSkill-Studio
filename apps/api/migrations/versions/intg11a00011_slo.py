"""SAML Single Logout URL on SSO connections (ADR-018 §5.2, R88)

Revision ID: intg11a00011
Revises: intg10a00010
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op

revision = "intg11a00011"
down_revision = "intg10a00010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_sso_connections",
        sa.Column("idp_slo_url", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("intg_sso_connections", "idp_slo_url")

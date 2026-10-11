"""OIDC PKCE S256 (ADR-018 §8, R135 — RFC 9700 requires PKCE for all clients)

Revision ID: intg14a00014
Revises: intg13a00013
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op

revision = "intg14a00014"
down_revision = "intg13a00013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "intg_sso_login_states",
        sa.Column("code_verifier", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("intg_sso_login_states", "code_verifier")

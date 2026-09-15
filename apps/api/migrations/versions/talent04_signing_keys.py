"""talent04 — Org signing keys for W3C VC / Open Badges 3.0.

Revision ID: talent04a00004
Revises: talent03a00003
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "talent04a00004"
down_revision = "talent03a00003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "talent_org_signing_keys",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "key_type",
            sa.String(20),
            nullable=False,
            server_default="ed25519",
        ),
        sa.Column("public_key", sa.String(500), nullable=False),
        sa.Column("private_key_encrypted", sa.String(500), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_talent_org_signing_keys_org",
        "talent_org_signing_keys",
        ["org_id", "status"],
    )


def downgrade():
    op.drop_index("ix_talent_org_signing_keys_org")
    op.drop_table("talent_org_signing_keys")

"""Integration fabric core: providers, connections, credentials (ADR-018 §4, P1)

Revision ID: intg01a00001
Revises: exp17a00017
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg01a00001"
down_revision = "exp17a00017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_providers",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("auth_mode", sa.String(30), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("capabilities", JSONB, nullable=False, server_default="[]"),
        sa.Column("config_schema", JSONB, nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "intg_connections",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "provider_id",
            sa.String(26),
            sa.ForeignKey("intg_providers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("provider_version", sa.Integer, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("config", JSONB, nullable=False, server_default="{}"),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("health", JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intg_conn_org", "intg_connections", ["org_id", "status"])
    op.create_index("uq_intg_conn_org_name", "intg_connections", ["org_id", "name"], unique=True)
    op.create_table(
        "intg_connection_credentials",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "connection_id",
            sa.String(26),
            sa.ForeignKey("intg_connections.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("ciphertext", sa.Text, nullable=False),
        sa.Column("key_version", sa.Integer, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rotated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("intg_connection_credentials")
    op.drop_index("uq_intg_conn_org_name", table_name="intg_connections")
    op.drop_index("ix_intg_conn_org", table_name="intg_connections")
    op.drop_table("intg_connections")
    op.drop_table("intg_providers")

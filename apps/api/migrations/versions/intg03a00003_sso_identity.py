"""Enterprise SSO + identity resolution: org domains, SSO connections, login
states, identity links, match queue, break-glass members (ADR-018 §5/§9, P3)

Revision ID: intg03a00003
Revises: intg02a00002
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg03a00003"
down_revision = "intg02a00002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_org_domains",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("verification_token", sa.String(64), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_domain_verified",
        "intg_org_domains",
        ["domain"],
        unique=True,
        postgresql_where=sa.text("status = 'verified'"),
    )
    op.create_index(
        "uq_intg_domain_org", "intg_org_domains", ["org_id", "domain"], unique=True
    )

    op.create_table(
        "intg_sso_connections",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("protocol", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("oidc_issuer", sa.String(500), nullable=True),
        sa.Column("oidc_client_id", sa.String(255), nullable=True),
        sa.Column("oidc_client_secret_ct", sa.Text, nullable=True),
        sa.Column("idp_entity_id", sa.String(500), nullable=True),
        sa.Column("idp_metadata_url", sa.String(500), nullable=True),
        sa.Column("idp_sso_url", sa.String(500), nullable=True),
        sa.Column("idp_certificates", JSONB, nullable=False, server_default="[]"),
        sa.Column("attribute_map", JSONB, nullable=False, server_default="{}"),
        sa.Column("enforce_sso", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("allow_jit", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("default_role", sa.String(30), nullable=False, server_default="'student'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intg_sso_org", "intg_sso_connections", ["org_id", "status"])

    op.create_table(
        "intg_sso_login_states",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "sso_connection_id",
            sa.String(26),
            sa.ForeignKey("intg_sso_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nonce", sa.String(64), nullable=False),
        sa.Column("redirect_to", sa.String(500), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intg_sso_state_expiry", "intg_sso_login_states", ["expires_at"])

    op.create_table(
        "intg_identity_links",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("connection_ref", sa.String(26), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("email_at_link", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_intg_idlink_subject",
        "intg_identity_links",
        ["connection_ref", "subject"],
        unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_index("ix_intg_idlink_org_user", "intg_identity_links", ["org_id", "user_id"])

    op.create_table(
        "intg_identity_match_queue",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("connection_ref", sa.String(26), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("payload", JSONB, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "resolved_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_intg_idqueue_org_status", "intg_identity_match_queue", ["org_id", "status"]
    )

    op.add_column(
        "org_members",
        sa.Column("is_break_glass", sa.Boolean, nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("org_members", "is_break_glass")
    op.drop_index("ix_intg_idqueue_org_status", table_name="intg_identity_match_queue")
    op.drop_table("intg_identity_match_queue")
    op.drop_index("ix_intg_idlink_org_user", table_name="intg_identity_links")
    op.drop_index("uq_intg_idlink_subject", table_name="intg_identity_links")
    op.drop_table("intg_identity_links")
    op.drop_index("ix_intg_sso_state_expiry", table_name="intg_sso_login_states")
    op.drop_table("intg_sso_login_states")
    op.drop_index("ix_intg_sso_org", table_name="intg_sso_connections")
    op.drop_table("intg_sso_connections")
    op.drop_index("uq_intg_domain_org", table_name="intg_org_domains")
    op.drop_index("uq_intg_domain_verified", table_name="intg_org_domains")
    op.drop_table("intg_org_domains")

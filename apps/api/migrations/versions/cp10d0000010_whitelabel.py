"""Control plane: branding, domains, blueprints, provision runs, exports
(Issue #27, ADR-014 §10).

Revision ID: cp10d0000010
Revises: cp09c0000009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "cp10d0000010"
down_revision: str | None = "cp09c0000009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_tenant_brandings",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False, unique=True),
        sa.Column("product_display_name", sa.String(100), nullable=True),
        sa.Column("logo_key", sa.String(500), nullable=True),
        sa.Column("favicon_key", sa.String(500), nullable=True),
        sa.Column("theme_tokens", JSONB(), nullable=False, server_default="{}"),
        sa.Column("login_tagline", sa.String(200), nullable=True),
        sa.Column("email_from_name", sa.String(100), nullable=True),
        sa.Column("email_footer", sa.String(500), nullable=True),
        sa.Column("certificate_footer", sa.String(300), nullable=True),
        sa.Column("support_email", sa.String(255), nullable=True),
        sa.Column("support_url", sa.String(500), nullable=True),
        sa.Column("legal_links", JSONB(), nullable=False, server_default="[]"),
        sa.Column("updated_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "cp_tenant_domains",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("hostname", sa.String(253), nullable=False, unique=True),
        sa.Column("status", sa.String(25), nullable=False, server_default="pending_verification"),
        sa.Column("verification_token_hash", sa.String(64), nullable=False),
        sa.Column("verification_method", sa.String(10), nullable=False, server_default="dns_txt"),
        sa.Column("verify_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(300), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("tls_status", sa.String(15), nullable=False, server_default="unmanaged"),
        sa.Column("tls_ref", sa.String(200), nullable=True),
        sa.Column("tls_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cp_domains_tenant", "cp_tenant_domains", ["tenant_id"])
    op.create_index(
        "uq_cp_domain_primary",
        "cp_tenant_domains",
        ["tenant_id"],
        unique=True,
        postgresql_where=sa.text("is_primary"),
    )
    op.create_table(
        "cp_tenant_blueprints",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("config", JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "cp_provision_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("blueprint_id", sa.String(26), nullable=True),
        sa.Column("tenant_id", sa.String(26), nullable=True),
        sa.Column("requested_name", sa.String(200), nullable=False),
        sa.Column("requested_slug", sa.String(100), nullable=False),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("status", sa.String(10), nullable=False, server_default="pending"),
        sa.Column("steps", JSONB(), nullable=False, server_default="[]"),
        sa.Column("idempotency_key", sa.String(120), nullable=False, unique=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "cp_tenant_exports",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="pending"),
        sa.Column("file_key", sa.String(500), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("cp_tenant_exports")
    op.drop_table("cp_provision_runs")
    op.drop_table("cp_tenant_blueprints")
    op.drop_table("cp_tenant_domains")
    op.drop_table("cp_tenant_brandings")

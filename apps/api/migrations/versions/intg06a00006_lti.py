"""LTI 1.3 tool side: registrations, deployments, resource links, launch
states, tool keys (ADR-018 §8, P7a)

Revision ID: intg06a00006
Revises: intg05a00005
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg06a00006"
down_revision = "intg05a00005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_lti_registrations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("issuer", sa.String(500), nullable=False),
        sa.Column("client_id", sa.String(255), nullable=False),
        sa.Column("auth_login_url", sa.String(500), nullable=False),
        sa.Column("auth_token_url", sa.String(500), nullable=False),
        sa.Column("jwks_url", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("allow_jit", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("default_role", sa.String(30), nullable=False, server_default="'student'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_lti_reg", "intg_lti_registrations", ["issuer", "client_id"], unique=True
    )
    op.create_index("ix_intg_lti_reg_org", "intg_lti_registrations", ["org_id"])

    op.create_table(
        "intg_lti_deployments",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "registration_id",
            sa.String(26),
            sa.ForeignKey("intg_lti_registrations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("deployment_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_lti_deploy",
        "intg_lti_deployments",
        ["registration_id", "deployment_id"],
        unique=True,
    )

    op.create_table(
        "intg_lti_resource_links",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "registration_id",
            sa.String(26),
            sa.ForeignKey("intg_lti_registrations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("deployment_id", sa.String(255), nullable=False),
        sa.Column("resource_link_id", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("ags_lineitem_url", sa.String(500), nullable=True),
        sa.Column("grade_sync_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_lti_rlink",
        "intg_lti_resource_links",
        ["registration_id", "deployment_id", "resource_link_id"],
        unique=True,
    )

    op.create_table(
        "intg_lti_launch_states",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "registration_id",
            sa.String(26),
            sa.ForeignKey("intg_lti_registrations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nonce", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intg_lti_state_expiry", "intg_lti_launch_states", ["expires_at"])

    op.create_table(
        "intg_lti_tool_keys",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("kid", sa.String(64), nullable=False, unique=True),
        sa.Column("private_pem_ct", sa.Text, nullable=False),
        sa.Column("public_jwk", JSONB, nullable=False, server_default="{}"),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("intg_lti_tool_keys")
    op.drop_index("ix_intg_lti_state_expiry", table_name="intg_lti_launch_states")
    op.drop_table("intg_lti_launch_states")
    op.drop_index("uq_intg_lti_rlink", table_name="intg_lti_resource_links")
    op.drop_table("intg_lti_resource_links")
    op.drop_index("uq_intg_lti_deploy", table_name="intg_lti_deployments")
    op.drop_table("intg_lti_deployments")
    op.drop_index("ix_intg_lti_reg_org", table_name="intg_lti_registrations")
    op.drop_index("uq_intg_lti_reg", table_name="intg_lti_registrations")
    op.drop_table("intg_lti_registrations")

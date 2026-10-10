"""SCIM 2.0 provisioning: tokens, groups, group members (ADR-018 §5.3, P4)

Revision ID: intg04a00004
Revises: intg03a00003
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg04a00004"
down_revision = "intg03a00003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_scim_tokens",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("group_map", JSONB, nullable=False, server_default="{}"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_intg_scim_tokens_org", "intg_scim_tokens", ["org_id", "revoked_at"])

    op.create_table(
        "intg_scim_groups",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_scim_group_org_name",
        "intg_scim_groups",
        ["org_id", "display_name"],
        unique=True,
    )

    op.create_table(
        "intg_scim_group_members",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "group_id",
            sa.String(26),
            sa.ForeignKey("intg_scim_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_scim_gm", "intg_scim_group_members", ["group_id", "user_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("uq_intg_scim_gm", table_name="intg_scim_group_members")
    op.drop_table("intg_scim_group_members")
    op.drop_index("uq_intg_scim_group_org_name", table_name="intg_scim_groups")
    op.drop_table("intg_scim_groups")
    op.drop_index("ix_intg_scim_tokens_org", table_name="intg_scim_tokens")
    op.drop_table("intg_scim_tokens")

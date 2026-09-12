"""Control plane: partners, revenue-share rules/entries, settlement
statements (Issue #27, ADR-014 §7).

Revision ID: cp07a0000007
Revises: cp06f0000006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "cp07a0000007"
down_revision: str | None = "cp06f0000006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_partners",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("partner_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(15), nullable=False, server_default="active"),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "cp_partner_members",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "partner_id",
            sa.String(26),
            sa.ForeignKey("cp_partners.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_partner_member", "cp_partner_members", ["partner_id", "user_id"], unique=True
    )
    op.create_table(
        "cp_revshare_rules",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("beneficiary_type", sa.String(12), nullable=False),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("revenue_type", sa.String(15), nullable=False),
        sa.Column("tenant_id", sa.String(26), nullable=True),
        sa.Column("plan_id", sa.String(26), nullable=True),
        sa.Column("listing_id", sa.String(26), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("rule_type", sa.String(40), nullable=False),
        sa.Column("rate", sa.Numeric(9, 6), nullable=True),
        sa.Column("amount_minor", sa.BigInteger(), nullable=True),
        sa.Column("amount_currency", sa.String(3), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="draft"),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_cp_revshare_rule_version ON cp_revshare_rules "
        "(coalesce(partner_id, ''), beneficiary_type, revenue_type, "
        "coalesce(tenant_id, ''), coalesce(plan_id, ''), coalesce(listing_id, ''), "
        "coalesce(country, ''), version)"
    )
    op.create_index("ix_cp_revshare_rules_partner", "cp_revshare_rules", ["partner_id", "status"])
    op.create_table(
        "cp_revshare_entries",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("beneficiary_type", sa.String(12), nullable=False),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("beneficiary_org_id", sa.String(26), nullable=True),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_id", sa.String(26), nullable=False),
        sa.Column("rule_id", sa.String(26), nullable=True),
        sa.Column("rule_snapshot", JSONB(), nullable=False),
        sa.Column("revenue_base_minor", sa.BigInteger(), nullable=False),
        sa.Column("share_amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("fx_rate_snapshot", JSONB(), nullable=True),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="accrued"),
        sa.Column("adjustment_of_id", sa.String(26), nullable=True),
        sa.Column("statement_id", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_cp_revshare_natural ON cp_revshare_entries "
        "(source_type, source_id, beneficiary_type, coalesce(partner_id, ''), "
        "coalesce(beneficiary_org_id, ''), coalesce(adjustment_of_id, ''))"
    )
    op.create_index(
        "ix_cp_revshare_partner_period",
        "cp_revshare_entries",
        ["partner_id", "period", "status"],
    )
    op.create_index(
        "ix_cp_revshare_org_period", "cp_revshare_entries", ["beneficiary_org_id", "period"]
    )
    op.create_index("ix_cp_revshare_statement", "cp_revshare_entries", ["statement_id"])
    op.create_table(
        "cp_settlement_statements",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("beneficiary_type", sa.String(12), nullable=False),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("beneficiary_org_id", sa.String(26), nullable=True),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("status", sa.String(15), nullable=False, server_default="draft"),
        sa.Column("opening_adjustments_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("gross_revenue_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("refunds_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("share_total_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("manual_adjustments_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("net_amount_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("finalized_by", sa.String(26), nullable=True),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(26), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_payment_ref", sa.String(120), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_cp_statement ON cp_settlement_statements "
        "(beneficiary_type, coalesce(partner_id, ''), coalesce(beneficiary_org_id, ''), period)"
    )


def downgrade() -> None:
    op.drop_table("cp_settlement_statements")
    op.drop_table("cp_revshare_entries")
    op.drop_table("cp_revshare_rules")
    op.drop_table("cp_partner_members")
    op.drop_table("cp_partners")

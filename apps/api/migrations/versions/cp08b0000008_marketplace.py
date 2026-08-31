"""Control plane: marketplace listings, purchases, license grants
(Issue #27, ADR-014 §8).

Revision ID: cp08b0000008
Revises: cp07a0000007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "cp08b0000008"
down_revision: str | None = "cp07a0000007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_marketplace_listings",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("product_type", sa.String(15), nullable=False),
        sa.Column("product_id", sa.String(26), nullable=False),
        sa.Column("seller_org_id", sa.String(26), nullable=False),
        sa.Column("seller_tenant_id", sa.String(26), nullable=False),
        sa.Column("offer_type", sa.String(20), nullable=False),
        sa.Column("price_minor", sa.BigInteger(), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("license_scope", sa.String(15), nullable=False, server_default="organization"),
        sa.Column("seat_limit", sa.Integer(), nullable=True),
        sa.Column("upgrade_policy", sa.String(15), nullable=False, server_default="all_versions"),
        sa.Column("platform_commission_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("included_plan_keys", JSONB(), nullable=False, server_default="[]"),
        sa.Column("bill_via_invoice", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(12), nullable=False, server_default="draft"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_listing_product",
        "cp_marketplace_listings",
        ["product_type", "product_id"],
        unique=True,
    )
    op.create_index("ix_cp_listings_seller", "cp_marketplace_listings", ["seller_tenant_id"])
    op.create_index("ix_cp_listings_offer", "cp_marketplace_listings", ["offer_type", "status"])
    op.create_table(
        "cp_marketplace_purchases",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "listing_id",
            sa.String(26),
            sa.ForeignKey("cp_marketplace_listings.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("buyer_tenant_id", sa.String(26), nullable=False),
        sa.Column("buyer_org_id", sa.String(26), nullable=False),
        sa.Column("purchaser_user_id", sa.String(26), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="pending"),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("platform_fee_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("seller_share_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("partner_share_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("economics_snapshot", JSONB(), nullable=False),
        sa.Column("payment_method", sa.String(20), nullable=True),
        sa.Column("payment_ref", sa.String(120), nullable=True),
        sa.Column("invoice_id", sa.String(26), nullable=True),
        sa.Column("idempotency_key", sa.String(120), nullable=True),
        sa.Column("refund_reason", sa.String(500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_purchase_idem",
        "cp_marketplace_purchases",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.create_index(
        "ix_cp_purchases_buyer", "cp_marketplace_purchases", ["buyer_tenant_id", "status"]
    )
    op.create_index("ix_cp_purchases_listing", "cp_marketplace_purchases", ["listing_id"])
    op.create_table(
        "cp_license_grants",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("listing_id", sa.String(26), nullable=True),
        sa.Column("product_type", sa.String(15), nullable=False),
        sa.Column("product_id", sa.String(26), nullable=False),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("org_id", sa.String(26), nullable=True),
        sa.Column("cohort_id", sa.String(26), nullable=True),
        sa.Column("scope", sa.String(15), nullable=False),
        sa.Column("seat_limit", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column("source", sa.String(15), nullable=False),
        sa.Column("purchase_id", sa.String(26), nullable=True),
        sa.Column("granted_by", sa.String(26), nullable=True),
        sa.Column("purchased_major", sa.Integer(), nullable=True),
        sa.Column(
            "starts_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.String(500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_cp_grants_lookup",
        "cp_license_grants",
        ["tenant_id", "product_type", "product_id", "status"],
    )
    op.create_index("ix_cp_grants_org", "cp_license_grants", ["org_id", "status"])
    op.create_index("ix_cp_grants_purchase", "cp_license_grants", ["purchase_id"])


def downgrade() -> None:
    op.drop_table("cp_license_grants")
    op.drop_table("cp_marketplace_purchases")
    op.drop_table("cp_marketplace_listings")

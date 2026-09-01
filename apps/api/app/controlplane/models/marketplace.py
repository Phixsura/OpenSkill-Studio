"""Marketplace listings, purchases, license grants (ADR-014 §8)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

PRODUCT_TYPES = frozenset({"skill_pack", "workflow_pack", "learning_path"})
OFFER_TYPES = frozenset({"free", "paid", "private", "partner_only", "included_with_plan"})
LICENSE_SCOPES = frozenset({"tenant", "organization", "cohort", "seat_limited"})


class MarketplaceListing(Base):
    __tablename__ = "cp_marketplace_listings"
    __table_args__ = (
        Index("uq_cp_listing_product", "product_type", "product_id", unique=True),
        Index("ix_cp_listings_seller", "seller_tenant_id"),
        Index("ix_cp_listings_offer", "offer_type", "status"),
    )

    id: Mapped[str] = ulid_pk()
    product_type: Mapped[str] = mapped_column(String(15), nullable=False)
    product_id: Mapped[str] = mapped_column(String(26), nullable=False)  # loose ref
    seller_org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    seller_tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    offer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    price_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    license_scope: Mapped[str] = mapped_column(
        String(15), default="organization", server_default="organization"
    )
    seat_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    upgrade_policy: Mapped[str] = mapped_column(
        String(15), default="all_versions", server_default="all_versions"
    )  # all_versions | major_locked
    # Snapshot of the platform default at create; per-listing change is a
    # platform_admin action (audited listing.commission_changed)
    platform_commission_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    included_plan_keys: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    bill_via_invoice: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    status: Mapped[str] = mapped_column(
        String(12), default="draft", server_default="draft"
    )  # draft | active | suspended | delisted
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MarketplacePurchase(Base):
    __tablename__ = "cp_marketplace_purchases"
    __table_args__ = (
        Index(
            "uq_cp_purchase_idem",
            "buyer_tenant_id",
            "idempotency_key",
            unique=True,
            postgresql_where="idempotency_key IS NOT NULL",
        ),
        Index("ix_cp_purchases_buyer", "buyer_tenant_id", "status"),
        Index("ix_cp_purchases_listing", "listing_id"),
    )

    id: Mapped[str] = ulid_pk()
    listing_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_marketplace_listings.id", ondelete="RESTRICT"), nullable=False
    )
    buyer_tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    buyer_org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    purchaser_user_id: Mapped[str] = mapped_column(String(26), nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), default="pending", server_default="pending"
    )  # pending | paid | failed | refunded
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    platform_fee_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    seller_share_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    partner_share_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    economics_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    invoice_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    refund_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LicenseGrant(Base):
    __tablename__ = "cp_license_grants"
    __table_args__ = (
        Index("ix_cp_grants_lookup", "tenant_id", "product_type", "product_id", "status"),
        Index("ix_cp_grants_org", "org_id", "status"),
        Index("ix_cp_grants_purchase", "purchase_id"),
    )

    id: Mapped[str] = ulid_pk()
    listing_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    product_type: Mapped[str] = mapped_column(String(15), nullable=False)
    product_id: Mapped[str] = mapped_column(String(26), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    org_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    cohort_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    scope: Mapped[str] = mapped_column(String(15), nullable=False)
    seat_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(10), default="active", server_default="active"
    )  # active | revoked | expired
    source: Mapped[str] = mapped_column(
        String(15), nullable=False
    )  # purchase | manual_grant | plan_included
    purchase_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    granted_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # Purchased-at latest major version (major_locked upgrade gating)
    purchased_major: Mapped[int | None] = mapped_column(Integer, nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoke_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

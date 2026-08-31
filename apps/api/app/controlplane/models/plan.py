"""Product plans, immutable plan versions, prices, entitlement overrides
(ADR-014 §2)."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class ProductPlan(Base):
    __tablename__ = "cp_product_plans"

    id: Mapped[str] = ulid_pk()
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # inactive = not newly subscribable; existing subscriptions unaffected
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PlanVersion(Base):
    """Immutable once active. Subscriptions FK a version, so history keeps
    the exact entitlement/pricing snapshot it was sold under."""

    __tablename__ = "cp_plan_versions"
    __table_args__ = (
        Index("uq_cp_plan_version", "plan_id", "version", unique=True),
        # One active version per plan at any moment
        Index(
            "uq_cp_plan_active",
            "plan_id",
            unique=True,
            postgresql_where="status = 'active'",
        ),
    )

    id: Mapped[str] = ulid_pk()
    plan_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_product_plans.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), default="draft", server_default="draft"
    )  # draft | active | retired
    # {entitlement_key: value} — per-key type-validated against ENTITLEMENT_DEFS
    entitlements: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PlanPrice(Base):
    """Frozen with its version (except external_price_ref — the one ADR-noted
    mutable field, backfilled after creating the price in Stripe)."""

    __tablename__ = "cp_plan_prices"
    __table_args__ = (
        Index("uq_cp_plan_price", "plan_version_id", "currency", "interval", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    plan_version_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_plan_versions.id", ondelete="CASCADE"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    interval: Mapped[str] = mapped_column(String(10), nullable=False)  # month | year
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    included_seats: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    overage_seat_amount_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    external_price_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TenantEntitlementOverride(Base):
    __tablename__ = "cp_entitlement_overrides"
    __table_args__ = (Index("uq_cp_ent_override", "tenant_id", "key", unique=True),)

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_tenant_accounts.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(60), nullable=False)  # must be in ENTITLEMENT_DEFS
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)  # {"v": <typed value>}
    enforcement: Mapped[str] = mapped_column(
        String(10), default="hard", server_default="hard"
    )  # hard | soft (numeric only)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

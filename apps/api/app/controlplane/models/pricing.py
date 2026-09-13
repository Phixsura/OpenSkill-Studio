"""Cost catalog, sell-price policies, rated usage, FX (ADR-014 §4).

Immutability rules:
- ProviderCostRate: supersede-only (the single legal UPDATE sets
  effective_until once); content edits create new rows.
- PricePolicy: only is_active/effective_until may change; content changes
  are new rows.
- RatedUsage: one row per usage event, snapshots frozen at rating time —
  historical margin stays reproducible after any catalog change (issue §13).
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Currency → minor-unit multiplier (v1 supports 0- and 2-decimal currencies).
CURRENCY_MINOR: dict[str, int] = {"JPY": 1, "KRW": 1}
DEFAULT_MINOR = 100


def minor_multiplier(currency: str) -> int:
    # R81[0]: normalize case — Stripe webhooks send LOWERCASE currency codes
    # ('jpy'), and a raw dict miss fell through to ×100, over-crediting
    # zero-decimal (JPY/KRW) top-ups 100x. _stripe_factor already uppercases;
    # this side must match.
    return CURRENCY_MINOR.get(currency.upper(), DEFAULT_MINOR)


POLICY_TYPES = frozenset(
    {
        "cost_plus_percentage",
        "cost_plus_fixed",
        "fixed_unit_price",
        "included_quota_then_overage",
    }
)


class ProviderCostRate(Base):
    __tablename__ = "cp_provider_cost_rates"
    __table_args__ = (
        Index(
            "ix_cp_cost_rates_lookup",
            "provider",
            "model_or_service",
            "usage_type",
            "effective_from",
        ),
    )

    id: Mapped[str] = ulid_pk()
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    # NULL = provider-level wildcard for the usage_type
    model_or_service: Mapped[str | None] = mapped_column(String(200), nullable=True)
    usage_type: Mapped[str] = mapped_column(String(40), nullable=False)
    capability_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # = canonical unit
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    # [{"min_qty": "0", "unit_cost": "0.018"}, …] — highest min_qty <= event qty wins
    tier_rules: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    minimum_fee_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PricePolicy(Base):
    __tablename__ = "cp_price_policies"
    __table_args__ = (
        Index("ix_cp_policies_tenant", "tenant_id", "usage_type", "effective_from"),
        Index("ix_cp_policies_plan", "plan_version_id", "usage_type"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(40), nullable=False)
    usage_type: Mapped[str | None] = mapped_column(String(40), nullable=True)  # NULL = all
    capability_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Specificity dims (loose refs; all NULL = global)
    plan_version_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False)  # per-type schema (§4.2)
    priority: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RatedUsage(Base):
    __tablename__ = "cp_rated_usage"
    __table_args__ = (
        Index("uq_cp_rated_event", "usage_event_id", unique=True),
        Index("ix_cp_rated_tenant_time", "tenant_id", "rated_at"),
        Index("ix_cp_rated_status_tenant", "status", "tenant_id"),
        Index(
            "ix_cp_rated_blocked",
            "status",
            postgresql_where="status = 'blocked'",
        ),
        # R50[44]: void_invoice unbind, margin accrual and invoice trace
        # all filter on invoice_line_id
        Index(
            "ix_cp_rated_invoice_line",
            "invoice_line_id",
            postgresql_where="invoice_line_id IS NOT NULL",
        ),
    )

    id: Mapped[str] = ulid_pk()
    usage_event_id: Mapped[str] = mapped_column(String(26), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    usage_type: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    cost_rate_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    cost_rate_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    internal_cost_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    internal_cost_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    price_policy_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    sell_rate_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    billable_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    # R75: EXACT fractional minor amounts, unrounded per event. billable/cost
    # *_minor above are the rounded-per-event integers kept for display/back-
    # compat, but any event whose marginal charge is < 0.5 minor rounds to 0 —
    # so charging must sum the EXACT columns and round ONCE (round-of-sum), not
    # sum the already-rounded integers (sum-of-rounded, which under-bills to 0).
    billable_amount_exact: Mapped[Decimal] = mapped_column(
        Numeric(24, 8), nullable=False, default=0, server_default="0"
    )
    internal_cost_exact: Mapped[Decimal] = mapped_column(
        Numeric(24, 8), nullable=False, default=0, server_default="0"
    )
    billable_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    margin_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rating_version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    status: Mapped[str] = mapped_column(
        String(12), default="rated", server_default="rated"
    )  # rated | invoiced | settled | adjusted | voided | blocked
    # 'settled' = paid via a credit reservation at run.terminal; excluded from
    # period invoicing (already charged) but still real billable revenue.
    invoice_line_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    void_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FxRate(Base):
    __tablename__ = "cp_fx_rates"
    __table_args__ = (Index("ix_cp_fx_pair", "base_currency", "quote_currency", "effective_from"),)

    id: Mapped[str] = ulid_pk()
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)  # 1 base = rate quote
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="manual", server_default="manual")
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReconciliationReport(Base):
    __tablename__ = "cp_reconciliation_reports"

    id: Mapped[str] = ulid_pk()
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_or_service: Mapped[str | None] = mapped_column(String(200), nullable=True)
    usage_type: Mapped[str] = mapped_column(String(40), nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # "2026-09"
    provider_reported_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    provider_reported_cost_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    platform_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    platform_cost_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    delta_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    delta_cost_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(10), default="open", server_default="open")
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resolved_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

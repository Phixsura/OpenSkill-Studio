"""Partners, revenue-share rules/entries, settlement statements
(ADR-014 §7)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

PARTNER_TYPES = frozenset(
    {
        "reseller",
        "regional_operator",
        "school_channel",
        "content_partner",
        "workflow_partner",
        "referral",
    }
)

RULE_TYPES = frozenset(
    {
        "percentage_of_net_revenue",
        "percentage_of_gross_revenue",
        "fixed_amount_per_unit",
        "fixed_amount_per_seat",
        "percentage_of_margin",
    }
)


class Partner(Base):
    __tablename__ = "cp_partners"

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    partner_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(15), default="active", server_default="active"
    )  # active | suspended | terminated
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", server_default="USD")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PartnerMember(Base):
    __tablename__ = "cp_partner_members"
    __table_args__ = (Index("uq_cp_partner_member", "partner_id", "user_id", unique=True),)

    id: Mapped[str] = ulid_pk()
    partner_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_partners.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False)  # admin | member
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RevenueShareRule(Base):
    """Versioned; immutable once active. Activating v(n+1) retires v(n) in
    the same tx. Accrued entries are NEVER recomputed (issue §23)."""

    __tablename__ = "cp_revshare_rules"
    __table_args__ = (
        Index(
            "uq_cp_revshare_rule_version",
            text("coalesce(partner_id, '')"),
            text("beneficiary_type"),
            text("revenue_type"),
            text("coalesce(tenant_id, '')"),
            text("coalesce(plan_id, '')"),
            text("coalesce(listing_id, '')"),
            text("coalesce(country, '')"),
            text("version"),
            unique=True,
        ),
        Index("ix_cp_revshare_rules_partner", "partner_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    beneficiary_type: Mapped[str] = mapped_column(String(12), nullable=False)  # partner|seller_org
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    revenue_type: Mapped[str] = mapped_column(
        String(15), nullable=False
    )  # subscription | usage | marketplace | all
    # Match dims (NULL = wildcard)
    tenant_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    plan_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    listing_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    rule_type: Mapped[str] = mapped_column(String(40), nullable=False)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)  # XOR amount
    amount_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    amount_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), default="draft", server_default="draft"
    )  # draft | active | retired
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RevenueShareEntry(Base):
    """Append-only accrual ledger with a natural-key uniqueness guard so
    replayed outbox messages can never double-accrue."""

    __tablename__ = "cp_revshare_entries"
    __table_args__ = (
        Index(
            "uq_cp_revshare_natural",
            text("source_type"),
            text("source_id"),
            text("beneficiary_type"),
            text("coalesce(partner_id, '')"),
            text("coalesce(beneficiary_org_id, '')"),
            text("coalesce(adjustment_of_id, '')"),
            unique=True,
        ),
        Index("ix_cp_revshare_partner_period", "partner_id", "period", "status"),
        Index("ix_cp_revshare_org_period", "beneficiary_org_id", "period"),
        Index("ix_cp_revshare_statement", "statement_id"),
    )

    id: Mapped[str] = ulid_pk()
    beneficiary_type: Mapped[str] = mapped_column(String(12), nullable=False)
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    beneficiary_org_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    source_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # invoice | invoice_line | marketplace_purchase | manual_adjustment
    source_id: Mapped[str] = mapped_column(String(26), nullable=False)
    rule_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    rule_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    revenue_base_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    share_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)  # signed
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # beneficiary currency
    fx_rate_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # "2026-09" (UTC month, ADR)
    status: Mapped[str] = mapped_column(
        String(10), default="accrued", server_default="accrued"
    )  # accrued | adjusted | approved | settled | voided
    adjustment_of_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    statement_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SettlementStatement(Base):
    __tablename__ = "cp_settlement_statements"
    __table_args__ = (
        Index(
            "uq_cp_statement",
            text("beneficiary_type"),
            text("coalesce(partner_id, '')"),
            text("coalesce(beneficiary_org_id, '')"),
            text("period"),
            unique=True,
        ),
    )

    id: Mapped[str] = ulid_pk()
    beneficiary_type: Mapped[str] = mapped_column(String(12), nullable=False)
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    beneficiary_org_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False)
    status: Mapped[str] = mapped_column(
        String(15), default="draft", server_default="draft"
    )  # draft | finalized | approved | paid_externally
    opening_adjustments_minor: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0"
    )
    gross_revenue_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    refunds_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    share_total_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    manual_adjustments_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    net_amount_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    finalized_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_payment_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

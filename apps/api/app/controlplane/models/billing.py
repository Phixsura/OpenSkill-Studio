"""Subscriptions, billing periods, invoices, payments, webhook events
(ADR-014 §6)."""

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
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

SUBSCRIPTION_LIVE_STATUSES = ("trial", "active", "past_due", "cancel_at_period_end")


class Subscription(Base):
    __tablename__ = "cp_subscriptions"
    __table_args__ = (
        # One live (non-cancelled) subscription per tenant
        Index(
            "uq_cp_sub_live",
            "tenant_id",
            unique=True,
            postgresql_where="status != 'cancelled'",
        ),
        Index("ix_cp_subs_tenant", "tenant_id"),
        Index("ix_cp_subs_period_end", "status", "current_period_end"),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    plan_version_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_plan_versions.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # trial | active | past_due | cancel_at_period_end | cancelled
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    interval: Mapped[str] = mapped_column(String(10), nullable=False)  # month | year
    seat_quantity: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider: Mapped[str] = mapped_column(String(20), default="manual", server_default="manual")
    external_customer_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SubscriptionChange(Base):
    """Append-only change log — the proration basis (ADR-014 §6.3)."""

    __tablename__ = "cp_subscription_changes"
    __table_args__ = (Index("ix_cp_sub_changes", "subscription_id", "effective_at"),)

    id: Mapped[str] = ulid_pk()
    subscription_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    change_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # plan_change | seat_change | cancel | reactivate | trial_convert
    from_plan_version_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    to_plan_version_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    from_seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    proration_mode: Mapped[str] = mapped_column(
        String(12), default="immediate", server_default="immediate"
    )  # immediate | next_period
    invoiced: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BillingPeriod(Base):
    __tablename__ = "cp_billing_periods"
    __table_args__ = (
        Index("uq_cp_period", "subscription_id", "period_start", unique=True),
        Index("ix_cp_periods_status", "status", "period_end"),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    subscription_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), default="open", server_default="open"
    )  # open | closed | invoiced
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Invoice(Base):
    __tablename__ = "cp_invoices"
    __table_args__ = (
        Index("ix_cp_invoices_tenant_status", "tenant_id", "status"),
        Index("ix_cp_invoices_due", "status", "due_at"),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    number: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    billing_period_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    status: Mapped[str] = mapped_column(
        String(15), default="draft", server_default="draft"
    )  # draft | open | paid | void | uncollectible
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    subtotal_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    credit_applied_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    tax_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    total_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    amount_due_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider: Mapped[str] = mapped_column(String(20), default="manual", server_default="manual")
    external_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    void_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class InvoiceLine(Base):
    """Immutable once the invoice is finalized (service-enforced)."""

    __tablename__ = "cp_invoice_lines"
    __table_args__ = (Index("ix_cp_invoice_lines", "invoice_id", "sort_order"),)

    id: Mapped[str] = ulid_pk()
    invoice_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_invoices.id", ondelete="CASCADE"), nullable=False
    )
    line_type: Mapped[str] = mapped_column(
        String(15), nullable=False
    )  # plan | seats | usage | license | proration | credit | adjustment | manual
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=1, server_default="1")
    unit_amount_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    usage_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CreditNote(Base):
    __tablename__ = "cp_credit_notes"

    id: Mapped[str] = ulid_pk()
    invoice_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_invoices.id", ondelete="RESTRICT"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), default="issued", server_default="issued"
    )  # issued | applied
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PaymentRecord(Base):
    __tablename__ = "cp_payment_records"
    __table_args__ = (
        # Provider double-delivery guard
        Index(
            "uq_cp_payment_external",
            "external_ref",
            "method",
            unique=True,
            postgresql_where="external_ref IS NOT NULL",
        ),
        Index("ix_cp_payments_tenant", "tenant_id"),
        Index("ix_cp_payments_invoice", "invoice_id"),
    )

    id: Mapped[str] = ulid_pk()
    invoice_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("cp_invoices.id", ondelete="RESTRICT"), nullable=True
    )
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    method: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # manual_bank_transfer | stripe | mock | credit_balance | other
    status: Mapped[str] = mapped_column(
        String(10), default="pending", server_default="pending"
    )  # pending | succeeded | failed | refunded
    external_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reference_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class InvoiceSequence(Base):
    """Per-year invoice number generator (FOR UPDATE in finalize)."""

    __tablename__ = "cp_invoice_sequences"

    scope: Mapped[str] = mapped_column(String(10), primary_key=True)  # "2026"
    last_value: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")


class BillingWebhookEvent(Base):
    """Replay guard: unique (provider, external_event_id)."""

    __tablename__ = "cp_billing_webhook_events"
    __table_args__ = (Index("uq_cp_webhook_event", "provider", "external_event_id", unique=True),)

    id: Mapped[str] = ulid_pk()
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    external_event_id: Mapped[str] = mapped_column(String(120), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    status: Mapped[str] = mapped_column(
        String(12), default="received", server_default="received"
    )  # received | processed | failed | duplicate | ignored
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

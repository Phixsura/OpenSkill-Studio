"""Credit ledger, reservations, budgets (ADR-014 §5).

Balance invariant enforced twice: FOR UPDATE critical section in the service
AND a DB CHECK constraint as the last line of defense against races.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

CREDIT_ENTRY_TYPES = frozenset(
    {
        "purchase",
        "promotional",
        "usage_debit",
        "refund",
        "adjustment",
        "expiration",
        "reservation_settle",
    }
)


class TenantCreditBalance(Base):
    """Lockable materialized balance — one row per (tenant, currency)."""

    __tablename__ = "cp_credit_balances"
    __table_args__ = (
        CheckConstraint(
            "balance_minor >= 0 AND reserved_minor >= 0 AND balance_minor >= reserved_minor",
            name="ck_cp_balance_nonneg",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(26), primary_key=True)
    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    balance_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    reserved_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CreditLedgerEntry(Base):
    """Append-only; balance_after_minor makes the ledger replayable."""

    __tablename__ = "cp_credit_ledger"
    __table_args__ = (
        Index(
            "uq_cp_credit_idem",
            "idempotency_key",
            unique=True,
            postgresql_where="idempotency_key IS NOT NULL",
        ),
        Index("ix_cp_credit_tenant_time", "tenant_id", "currency", "created_at"),
        Index(
            "ix_cp_credit_promo",
            "tenant_id",
            postgresql_where="entry_type = 'promotional'",
        ),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)  # signed
    balance_after_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consumed_expiration_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CreditReservation(Base):
    __tablename__ = "cp_credit_reservations"
    __table_args__ = (
        Index(
            "uq_cp_reservation_held",
            "reference_type",
            "reference_id",
            unique=True,
            postgresql_where="status = 'held'",
        ),
        Index("ix_cp_reservations_expiry", "status", "expires_at"),
        Index("ix_cp_reservations_tenant", "tenant_id"),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), default="held", server_default="held"
    )  # held | settled | released | expired
    reference_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_id: Mapped[str] = mapped_column(String(120), nullable=False)
    settled_amount_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    extension_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class BudgetPolicy(Base):
    __tablename__ = "cp_budget_policies"
    __table_args__ = (
        # Functional uniqueness across nullable dims (coalesce in raw DDL —
        # created in the migration; declared plainly here for autogenerate)
        Index(
            "uq_cp_budget_dims",
            text("tenant_id"),
            text("scope_type"),
            text("coalesce(scope_id, '')"),
            text("period"),
            text("coalesce(capability_key, '')"),
            text("coalesce(usage_type, '')"),
            unique=True,
        ),
        Index("ix_cp_budgets_tenant", "tenant_id", "is_active"),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    scope_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # tenant | org | project | cohort | user
    scope_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # NULL for tenant
    period: Mapped[str] = mapped_column(String(10), nullable=False)  # daily | monthly
    capability_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    usage_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    limit_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    warning_threshold_pct: Mapped[int] = mapped_column(Integer, default=80, server_default="80")
    hard_stop: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

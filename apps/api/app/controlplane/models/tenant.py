"""Tenant accounts, tenant members, platform roles, impersonation (ADR-014 §1).

TenantAccount is the commercial customer above Organization (the product
workspace). Every organization belongs to exactly one tenant
(organizations.tenant_id NOT NULL after the backfill migration).
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class TenantStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TenantAccountType(str, enum.Enum):
    DIRECT = "direct"
    PARTNER_MANAGED = "partner_managed"
    OEM = "oem"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"


# Allowed lifecycle transitions (from → {to}); enforced with conditional
# UPDATEs (0 rows updated == lost race → 409 TENANT_STATUS_CONFLICT).
TENANT_TRANSITIONS: dict[TenantStatus, set[TenantStatus]] = {
    TenantStatus.TRIAL: {TenantStatus.ACTIVE, TenantStatus.SUSPENDED, TenantStatus.CANCELLED},
    TenantStatus.ACTIVE: {
        TenantStatus.PAST_DUE,
        TenantStatus.SUSPENDED,
        TenantStatus.CANCELLED,
    },
    TenantStatus.PAST_DUE: {
        TenantStatus.ACTIVE,
        TenantStatus.SUSPENDED,
        TenantStatus.CANCELLED,
    },
    TenantStatus.SUSPENDED: {TenantStatus.ACTIVE, TenantStatus.CANCELLED},
    TenantStatus.CANCELLED: {TenantStatus.ARCHIVED},
    TenantStatus.ARCHIVED: set(),
}

# Statuses in which new costed/consuming activity is blocked server-side.
TENANT_BLOCKED_STATUSES = frozenset(
    {TenantStatus.SUSPENDED, TenantStatus.CANCELLED, TenantStatus.ARCHIVED}
)


class TenantAccount(Base):
    __tablename__ = "cp_tenant_accounts"
    __table_args__ = (
        Index("ix_cp_tenants_status", "status"),
        Index("ix_cp_tenants_partner", "partner_id"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus, name="cp_tenant_status", create_constraint=True),
        default=TenantStatus.TRIAL,
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    account_type: Mapped[TenantAccountType] = mapped_column(
        Enum(TenantAccountType, name="cp_tenant_account_type", create_constraint=True),
        default=TenantAccountType.DIRECT,
    )
    billing_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    # Settlement currency. Only platform_admin may change it, and only while
    # the tenant has no non-draft invoices (TENANT_CURRENCY_LOCKED 409).
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="USD")
    # Budget / billing period boundaries are computed in this timezone.
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, server_default="UTC")
    # Channel attribution (loose ref — partners land in P7).
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    attributed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspension_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Free-form flags, e.g. {"credit_enforcement": true}
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TenantMember(Base):
    """Tenant-scoped commercial roles (owner | billing_admin) — separate from
    org RBAC by design; a tenant owner is not automatically an org member."""

    __tablename__ = "cp_tenant_members"
    __table_args__ = (
        Index("uq_cp_tenant_member", "tenant_id", "user_id", unique=True),
        Index("ix_cp_tenant_members_user", "user_id"),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cp_tenant_accounts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(30), nullable=False)  # owner | billing_admin
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


TENANT_ROLES = frozenset({"owner", "billing_admin"})

PLATFORM_ROLES = frozenset({"platform_admin", "platform_support", "billing_admin"})


class PlatformRoleAssignment(Base):
    """Control-plane roles. UserRole.ADMIN keeps bootstrap access; these are
    the operational roles the platform team actually works with."""

    __tablename__ = "cp_platform_roles"
    __table_args__ = (Index("uq_cp_platform_role", "user_id", "role", unique=True),)

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    granted_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SupportImpersonationGrant(Base):
    """Auditable, short-lived, revocable support impersonation (ADR-014 §1.5).

    Tokens minted from a grant carry imp/imp_grant claims; the
    ImpersonationGuardMiddleware enforces read-only outside a tiny whitelist.
    """

    __tablename__ = "cp_impersonation_grants"
    __table_args__ = (
        Index("ix_cp_imp_grants_platform_user", "platform_user_id", "created_at"),
        Index("ix_cp_imp_grants_target", "target_user_id"),
    )

    id: Mapped[str] = ulid_pk()
    platform_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    target_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("cp_tenant_accounts.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

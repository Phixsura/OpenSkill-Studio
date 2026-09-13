"""Tenant branding, custom domains, blueprints, provision runs, exports
(ADR-014 §10)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Closed theme-token key set: hex colors + a bounded radius enum. Anything
# else is rejected at write time — no arbitrary CSS/HTML/JS ever.
THEME_COLOR_KEYS = frozenset({"primary", "accent", "background", "foreground", "muted", "border"})
THEME_RADIUS_VALUES = frozenset({"none", "sm", "md", "lg", "full"})


class TenantBranding(Base):
    __tablename__ = "cp_tenant_brandings"

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), unique=True, nullable=False)
    product_display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    logo_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    favicon_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    theme_tokens: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    login_tagline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email_from_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email_footer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    certificate_footer: Mapped[str | None] = mapped_column(String(300), nullable=True)
    support_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    support_url: Mapped[str | None] = mapped_column(String(500), nullable=True)  # https only
    legal_links: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    updated_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TenantDomain(Base):
    __tablename__ = "cp_tenant_domains"
    __table_args__ = (
        Index("ix_cp_domains_tenant", "tenant_id"),
        Index(
            "uq_cp_domain_primary",
            "tenant_id",
            unique=True,
            postgresql_where="is_primary",
        ),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    # Normalized: lowercase, idna punycode, no port/scheme/trailing dot.
    # UNIQUE across all tenants — a disabled domain still holds the name
    # (anti-sniping); DELETE frees it.
    hostname: Mapped[str] = mapped_column(String(253), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(25), default="pending_verification", server_default="pending_verification"
    )  # pending_verification | verified | active | failed | disabled
    verification_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    verification_method: Mapped[str] = mapped_column(
        String(10), default="dns_txt", server_default="dns_txt"
    )
    verify_attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    tls_status: Mapped[str] = mapped_column(
        String(15), default="unmanaged", server_default="unmanaged"
    )  # unmanaged | provisioning | active | failed
    tls_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tls_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TenantBlueprint(Base):
    """Config-only provisioning template (ADR-014 §10.3). The strict
    BlueprintConfig schema structurally cannot carry users/progress/
    submissions/credentials/billing — issue §8 red line."""

    __tablename__ = "cp_tenant_blueprints"

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # NULL = platform
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TenantProvisionRun(Base):
    """Idempotent, resumable provisioning step machine."""

    __tablename__ = "cp_provision_runs"

    id: Mapped[str] = ulid_pk()
    blueprint_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # set once created
    requested_name: Mapped[str] = mapped_column(String(200), nullable=False)
    requested_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    partner_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    status: Mapped[str] = mapped_column(
        String(10), default="pending", server_default="pending"
    )  # pending | running | completed | failed
    # [{"step", "status": done|failed, "error", "at"}] — step 0 snapshots config
    steps: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TenantExport(Base):
    __tablename__ = "cp_tenant_exports"

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str] = mapped_column(String(26), nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), default="pending", server_default="pending"
    )  # pending | completed | failed
    file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

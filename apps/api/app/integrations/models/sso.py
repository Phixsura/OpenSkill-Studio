"""Enterprise SSO models (ADR-018 §5.1/§5.2).

OrgDomain anchors tenant identity routing: only a VERIFIED domain may drive
IdP discovery, JIT provisioning or enforced SSO, and a domain can be verified
by at most one org globally (partial unique index). SsoConnection is one IdP
integration per org; certificates/secrets are pinned to the connection, never
shared. SsoLoginState is the single-use state/nonce row for the OIDC code
flow (DB-backed so tests need no Redis).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

DOMAIN_STATUSES = frozenset({"pending", "verified", "failed"})
SSO_PROTOCOLS = frozenset({"oidc", "saml"})
SSO_STATUSES = frozenset({"draft", "testing", "active", "disabled"})

# Public-mailbox domains can never anchor an org (JIT/routing off a freemail
# domain is an account-takeover vector — ADR-018 §5.1). In-repo denylist;
# deliberately conservative, extend as support tickets arrive.
PUBLIC_EMAIL_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "yahoo.com",
        "icloud.com",
        "me.com",
        "aol.com",
        "proton.me",
        "protonmail.com",
        "mail.com",
        "gmx.com",
        "qq.com",
        "163.com",
        "126.com",
        "foxmail.com",
        "sina.com",
        "yeah.net",
    }
)

# JIT may mint at most these roles (ADR §5.2: never owner/admin).
JIT_ALLOWED_ROLES = frozenset({"student", "instructor"})


class OrgDomain(Base):
    __tablename__ = "intg_org_domains"
    __table_args__ = (
        # One VERIFIED holder per domain globally; many pending claims OK.
        Index(
            "uq_intg_domain_verified",
            "domain",
            unique=True,
            postgresql_where="status = 'verified'",
        ),
        Index("uq_intg_domain_org", "org_id", "domain", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    verification_token: Mapped[str] = mapped_column(String(64), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SsoConnection(Base):
    __tablename__ = "intg_sso_connections"
    __table_args__ = (Index("ix_intg_sso_org", "org_id", "status"),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    protocol: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    # OIDC
    oidc_issuer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    oidc_client_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Client secret is write-only ciphertext (core/crypto.py envelope).
    oidc_client_secret_ct: Mapped[str | None] = mapped_column(Text, nullable=True)
    # SAML (P3b): metadata URL, entity id, pinned certificates
    idp_entity_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idp_metadata_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idp_sso_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idp_certificates: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    # {email: "...", display_name: "...", external_id: "..."} claim names
    attribute_map: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    enforce_sso: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_jit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_role: Mapped[str] = mapped_column(String(30), nullable=False, default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SsoLoginState(Base):
    """Single-use OIDC state/nonce (10-min TTL, consumed atomically)."""

    __tablename__ = "intg_sso_login_states"
    __table_args__ = (Index("ix_intg_sso_state_expiry", "expires_at"),)

    id: Mapped[str] = ulid_pk()  # the `state` value itself
    sso_connection_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_sso_connections.id", ondelete="CASCADE"), nullable=False
    )
    nonce: Mapped[str] = mapped_column(String(64), nullable=False)
    redirect_to: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

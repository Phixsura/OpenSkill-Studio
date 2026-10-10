"""Integration connections + write-only credentials (ADR-018 §4.2/§4.3)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

CONNECTION_STATUSES = frozenset({"pending", "active", "degraded", "disabled", "error"})

# Service-enforced transitions (§4.2). "degraded" flips automatically on
# consecutive failures and back on success; admins toggle disabled; a
# permanent auth rejection parks the connection in "error" until credentials
# are replaced (which resets to pending for a fresh ping).
CONNECTION_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"active", "disabled", "error"}),
    "active": frozenset({"degraded", "disabled", "error"}),
    "degraded": frozenset({"active", "disabled", "error"}),
    "disabled": frozenset({"pending"}),
    "error": frozenset({"pending", "disabled"}),
}

# Connections the scheduler/engine will touch.
SCHEDULABLE_STATUSES = frozenset({"active", "degraded"})

CREDENTIAL_KINDS = frozenset({"oauth2_tokens", "api_key", "basic", "client_secret"})

# consecutive_failures threshold that flips active -> degraded.
DEGRADE_AFTER_FAILURES = 3


class IntegrationConnection(Base):
    __tablename__ = "intg_connections"
    __table_args__ = (
        Index("ix_intg_conn_org", "org_id", "status"),
        Index("uq_intg_conn_org_name", "org_id", "name", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    provider_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_providers.id", ondelete="RESTRICT"), nullable=False
    )
    # Pinned at creation; changes only via the explicit upgrade endpoint.
    provider_version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # Validated against provider.config_schema (additionalProperties rejected).
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    # Provider instance URL (e.g. district OneRoster root). Egress-validated
    # at write AND again at every use (§14.1 — rebinding defense).
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # {last_ok_at, last_error_at, last_error_class, consecutive_failures}
    health: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class IntegrationConnectionCredential(Base):
    """Write-only credential envelope (1:1 with connection; rotate in place).

    ``ciphertext`` is a core/crypto.py Fernet token over a JSON blob
    (tokens/keys/expiry). No API response model carries this column —
    the credential response is exactly {id, kind, expires_at, rotated_at}.
    """

    __tablename__ = "intg_connection_credentials"

    id: Mapped[str] = ulid_pk()
    connection_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("intg_connections.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    key_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Plaintext expiry copy for refresh scheduling only — never the token.
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

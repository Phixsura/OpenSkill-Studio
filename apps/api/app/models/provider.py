"""Provider abstraction — four-entity split (ADR-011).

ProviderAdapter (platform code catalog) → ProviderConnection (org-scoped, credential
by reference) → ProviderModelOffering (the matchable unit) → OrgCredential
(envelope-encrypted, never returned by any API).

Credentials NEVER appear in workflow definitions, manifests, connection config
JSON, or exports — they are resolved late, inside the executor, by reference.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class ProviderAdapter(Base):
    """Platform-level adapter catalog entry (code implements the contract)."""

    __tablename__ = "provider_adapters"

    id: Mapped[str] = ulid_pk()
    key: Mapped[str] = mapped_column(String(64), unique=True)  # "mock", "anthropic"
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # JSON Schema for non-sensitive connection config fields
    config_schema: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Credential FIELD NAMES only (e.g. ["api_key"]) — never values
    credential_fields: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OrgCredential(Base):
    """Envelope-encrypted org credential. Write-only at the API layer."""

    __tablename__ = "org_credentials"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100))
    # Fernet-encrypted JSON of {field_name: value}; decrypted only by the executor
    encrypted_data: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_org_credentials_org", "org_id"),)


class ProviderConnection(Base):
    """Org-scoped connection to a provider (adapter + config + credential ref)."""

    __tablename__ = "provider_connections"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    adapter_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("provider_adapters.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100))
    # Non-sensitive config only; service layer rejects credential_fields keys here
    config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    credential_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("org_credentials.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    last_health_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    health_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_provider_conn_org", "org_id"),)


class ProviderModelOffering(Base):
    """The matchable unit: capability + model + features + limits + cost."""

    __tablename__ = "provider_model_offerings"

    id: Mapped[str] = ulid_pk()
    connection_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("provider_connections.id", ondelete="CASCADE")
    )
    # References capability_tags.key — loose string coupling (same as origin_* pattern)
    capability_key: Mapped[str] = mapped_column(String(64))
    model_name: Mapped[str] = mapped_column(String(200))
    features: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    limits: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    cost_per_call_usd: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    quality_tier: Mapped[str] = mapped_column(
        String(20), default="standard", server_default="standard"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_offering_capability", "capability_key"),
        Index("ix_offering_connection", "connection_id"),
    )

"""Integration provider catalog (ADR-018 §4.1).

Code-seeded rows (one per supported external system kind), the Nango
``providers.yaml`` analog. Connections pin ``version`` at creation —
catalog upgrades never silently change a live connection (Prismatic rule).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

PROVIDER_CATEGORIES = frozenset(
    {
        "identity",
        "roster",
        "lms",
        "hris",
        "ats",
        "crm",
        "storage",
        "messaging",
        "erp",
        "warehouse",
        "generic",
    }
)

AUTH_MODES = frozenset(
    {
        "oauth2_cc",
        "oauth2_ac",
        "api_key",
        "basic",
        "saml_metadata",
        "oidc_discovery",
        "none",
    }
)


class IntegrationProvider(Base):
    __tablename__ = "intg_providers"

    id: Mapped[str] = ulid_pk()
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    auth_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    # Capability keys this provider's connector declares (§13) — checked at
    # profile binding AND at every run start (R82 runtime re-check).
    capabilities: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    # JSON Schema for per-connection config; drives the setup wizard and
    # validates every config write (extra keys rejected).
    config_schema: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

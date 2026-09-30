"""Capability mapping + pricing/availability intelligence (ADR-016 Parts D, E)."""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Total order — upgrades in place, downgrades need force+admin (ADR-016 §3.4)
EVIDENCE_LEVELS = [
    "vendor_claimed",
    "platform_observed",
    "benchmark_verified",
    "production_verified",
    "human_verified",
]
EVIDENCE_RANK = {level: i for i, level in enumerate(EVIDENCE_LEVELS)}

PRICE_UNITS = frozenset(
    {
        "token_input",
        "token_output",
        "image",
        "megapixel",
        "video_second",
        "minute",
        "request",
        "subscription_month",
        "volume_tier",
    }
)

RECONCILIATION_STATUSES = frozenset(
    {"unreviewed", "under_review", "approved", "rejected", "superseded"}
)

AVAILABILITY_RECORD_TYPES = frozenset(
    {"rate_limit", "concurrency", "queue", "latency", "status", "deprecation", "sunset"}
)


class CapabilityMapping(Base):
    """Maps a canonical ecosystem entity to a platform capability with typed I/O."""

    __tablename__ = "eco_capability_mappings"

    id: Mapped[str] = ulid_pk()
    entity_kind: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    # Loose FK to capability_tags.key (ADR-011 pattern)
    capability_key: Mapped[str] = mapped_column(String(64))
    # vendor_claimed | platform_observed | benchmark_verified |
    # production_verified | human_verified
    evidence_level: Mapped[str] = mapped_column(
        String(30), default="vendor_claimed", server_default="vendor_claimed"
    )
    # {"inputs": [{"type": "image", "formats": ["png"], "max_mp": 25}],
    #  "outputs": [{"type": "video", "max_seconds": 10}], "constraints": {...}}
    io_spec: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=0.5)
    source_observation_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_observations.id", ondelete="SET NULL"), nullable=True
    )
    verified_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("entity_kind", "entity_id", "capability_key", name="uq_eco_cap_mapping"),
        Index("ix_eco_cap_mapping_key", "capability_key"),
        Index("ix_eco_cap_mapping_entity", "entity_kind", "entity_id"),
    )


class PriceObservation(Base):
    """Externally observed pricing — NEVER a billing rate until reconciled.

    Approval creates a new ProviderCostRate via the control-plane facade; this
    table never feeds billing directly (ADR-016 §3.5).
    """

    __tablename__ = "eco_price_observations"

    id: Mapped[str] = ulid_pk()
    observation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_observations.id", ondelete="RESTRICT")
    )
    entity_kind: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    region: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # token_input | token_output | image | megapixel | video_second | minute |
    # request | subscription_month | volume_tier
    unit: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Numeric(14, 6))
    currency: Mapped[str] = mapped_column(String(3), default="USD", server_default="USD")
    # Volume tier details: {"min_volume": 1000000, "max_volume": null}
    tier: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # unreviewed | under_review | approved | rejected | superseded
    reconciliation_status: Mapped[str] = mapped_column(
        String(20), default="unreviewed", server_default="unreviewed"
    )
    reconciled_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reconciled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Loose ref to cp_provider_cost_rates.id once approved
    approved_cost_rate_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_eco_price_obs_entity", "entity_kind", "entity_id", "observed_at"),
        Index("ix_eco_price_obs_status", "reconciliation_status"),
    )


class AvailabilityRecord(Base):
    """Regions, rate limits, latency, status, deprecation/sunset intelligence."""

    __tablename__ = "eco_availability_records"

    id: Mapped[str] = ulid_pk()
    entity_kind: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    region: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # rate_limit | concurrency | queue | latency | status | deprecation | sunset
    record_type: Mapped[str] = mapped_column(String(20))
    # e.g. {"requests_per_minute": 60} / {"p50_ms": 3400} / {"sunset_at": "..."}
    value: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source_observation_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_observations.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_eco_avail_entity", "entity_kind", "entity_id", "record_type", "observed_at"),
    )

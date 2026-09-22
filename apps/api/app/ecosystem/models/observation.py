"""Append-only observation ledger + typed change events (ADR-016 Part B).

Observations are NEVER updated or deleted. Corrections append a new row and
link the old one via superseded_by_id. Idempotency: (source, raw_hash,
event_type) is unique, so re-ingesting an unchanged payload is a no-op.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
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

OBSERVATION_EVENT_TYPES = frozenset(
    {
        "model_released",
        "model_deprecated",
        "price_changed",
        "api_changed",
        "limits_changed",
        "region_changed",
        "license_changed",
        "security_advisory",
        "workflow_dependency_changed",
        "release_published",
        "availability_changed",
        "catalog_snapshot",
    }
)

ENTITY_KINDS = frozenset(
    {"provider", "tool", "model", "model_version", "workflow", "agent", "node_package"}
)

EXTRACTION_METHODS = frozenset({"structured", "llm", "manual"})

CHANGE_TYPES = frozenset(
    {"price", "limits", "license", "api", "model_version", "lifecycle", "region", "security"}
)

CHANGE_SEVERITIES = frozenset(
    {"info", "update_available", "degraded", "breaking", "security_critical", "sunset_risk"}
)


class EcosystemObservation(Base):
    """One normalized external fact, with full provenance. Append-only."""

    __tablename__ = "eco_observations"

    id: Mapped[str] = ulid_pk()
    # RESTRICT: provenance must survive — a source with observations can only be archived
    source_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_sources.id", ondelete="RESTRICT")
    )
    sync_run_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_source_sync_runs.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(40))
    entity_kind: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Source-native identifier (e.g. "gpt-image-2", "org/repo")
    external_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Set after entity resolution — loose ref into the canonical catalog
    canonical_entity_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    canonical_entity_kind: Mapped[str | None] = mapped_column(String(30), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # When the change takes effect (future for announced sunsets)
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # SHA-256 of the raw payload — idempotency key together with source/event_type
    raw_hash: Mapped[str] = mapped_column(String(64))
    normalized: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    parser_version: Mapped[str] = mapped_column(String(20), default="1.0")
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=1.0)
    provenance_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # structured | llm | manual — LLM-extracted facts carry reduced confidence
    extraction_method: Mapped[str] = mapped_column(
        String(20), default="structured", server_default="structured"
    )
    human_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    verified_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Corrections chain: newer observation that supersedes this one
    superseded_by_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_observations.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("source_id", "raw_hash", "event_type", name="uq_eco_obs_idem"),
        Index("ix_eco_obs_event", "event_type", "observed_at"),
        Index("ix_eco_obs_entity", "canonical_entity_kind", "canonical_entity_id"),
        Index("ix_eco_obs_external_ref", "external_ref"),
    )


class ChangeEvent(Base):
    """A typed, structured change derived from observation diffs (not text diffs)."""

    __tablename__ = "eco_change_events"

    id: Mapped[str] = ulid_pk()
    observation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_observations.id", ondelete="RESTRICT")
    )
    # price | limits | license | api | model_version | lifecycle | region | security
    change_type: Mapped[str] = mapped_column(String(30))
    field: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # info | update_available | degraded | breaking | security_critical | sunset_risk
    severity: Mapped[str] = mapped_column(String(30), default="info", server_default="info")
    entity_kind: Mapped[str | None] = mapped_column(String(30), nullable=True)
    canonical_entity_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    acknowledged_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("ix_eco_changes_type", "change_type", "detected_at"),
        Index("ix_eco_changes_severity", "severity", "acknowledged"),
        Index("ix_eco_changes_entity", "entity_kind", "canonical_entity_id"),
    )

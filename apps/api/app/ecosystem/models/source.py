"""External source registry (ADR-016 Part A).

An EcosystemSource is a registered, attested feed of external AI ecosystem
facts. Sync is adapter-driven, rate-limited, size-capped and SSRF-guarded —
never unrestricted crawling.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

SOURCE_TYPES = frozenset(
    {
        "provider_api",
        "model_docs_feed",
        "github_repo",
        "huggingface",
        "comfyui_repo",
        "pricing_feed",
        "internal_research",
        "manual_analyst",
    }
)

TRUST_LEVELS = frozenset({"official", "verified_partner", "community", "unverified", "internal"})

SOURCE_STATUSES = frozenset({"active", "paused", "error", "archived"})

# Consecutive sync failures before the circuit breaker pauses the source
CIRCUIT_BREAKER_THRESHOLD = 5


class EcosystemSource(Base):
    """A registered external intelligence source."""

    __tablename__ = "eco_sources"

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), unique=True)
    source_type: Mapped[str] = mapped_column(String(40))
    trust_level: Mapped[str] = mapped_column(String(20), default="unverified")
    # Validated by the SSRF guard at write time; manual_analyst sources have none
    base_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    adapter_key: Mapped[str] = mapped_column(String(64))
    parser_version: Mapped[str] = mapped_column(String(20), default="1.0")
    # Non-sensitive adapter config only — credential FIELD NAMES, never values
    config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=1440, server_default="1440")
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=60, server_default="60")
    max_response_bytes: Mapped[int] = mapped_column(
        Integer, default=5_242_880, server_default="5242880"
    )
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30, server_default="30")
    # Conditional-GET state (RFC 7232)
    etag: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_modified: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Operator attestation that syncing this source respects robots/ToS
    robots_compliant: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_eco_sources_status", "status"),
        Index("ix_eco_sources_type", "source_type"),
    )


class SourceSyncRun(Base):
    """Audit record for a single sync attempt against a source."""

    __tablename__ = "eco_source_sync_runs"

    id: Mapped[str] = ulid_pk()
    source_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_sources.id", ondelete="CASCADE")
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # running | success | not_modified | failed | skipped
    status: Mapped[str] = mapped_column(String(20), default="running", server_default="running")
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bytes_fetched: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    observations_created: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    changes_detected: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    parser_version: Mapped[str] = mapped_column(String(20), default="1.0")

    __table_args__ = (Index("ix_eco_sync_runs_source", "source_id", "started_at"),)

class RawSnapshot(Base):
    """Retained raw payload for replay (ADR-016 §42, deps.dev reprocessing bar).

    One row per distinct (source, payload); size already bounded upstream by
    the source's max_response_bytes security guard. Pruned after 90 days by
    the retention cron — replay is a recent-history tool, not an archive.
    """

    __tablename__ = "eco_raw_snapshots"

    id: Mapped[str] = ulid_pk()
    source_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_sources.id", ondelete="CASCADE")
    )
    raw_hash: Mapped[str] = mapped_column(String(64))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    content_length: Mapped[int] = mapped_column(Integer)
    # Parser version that originally processed this payload
    parser_version: Mapped[str] = mapped_column(String(20))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("source_id", "raw_hash", name="uq_eco_raw_snapshot"),
        Index("ix_eco_raw_snapshots_source", "source_id", "fetched_at"),
    )

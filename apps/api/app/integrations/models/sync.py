"""Mapping profiles + sync engine state (ADR-018 §10/§11).

Deviation from §6.1 (noted in ADR §19): staging is ONE generic table
(intg_staged_records) discriminated by `model`, not a table per entity —
the engine, tombstone pass and conflict reporting are then written once and
cover roster/talent/CRM uniformly; provisioning passes read it by model.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

MAPPING_DIRECTIONS = frozenset({"inbound", "outbound"})

# Canonical models the fabric understands (payload schemas enforced at the
# mapping boundary — R86 import-validate rule). Extended by later phases.
CANONICAL_MODELS = frozenset(
    {
        "roster.term",
        "roster.class",
        "roster.enrollment",
        "roster.user",
        "talent.candidate",
        "talent.application",
        "talent.job",
        "crm.account",
        "crm.contact",
        "crm.deal",
    }
)

SYNC_DIRECTIONS = frozenset({"pull", "push", "bidirectional"})
SYNC_SCHEDULES = frozenset({"manual", "hourly", "daily"})
RUN_STATUSES = frozenset({"queued", "running", "succeeded", "failed", "cancelled", "partial"})
RUN_TRIGGERS = frozenset({"schedule", "manual", "webhook", "backfill"})
RECORD_OUTCOMES = frozenset(
    {"created", "updated", "unchanged", "tombstoned", "conflict", "error"}
)
CONFLICT_CLASSES = frozenset(
    {
        "ambiguous_identity",
        "duplicate_external_id",
        "missing_reference",
        "role_conflict",
        "date_invalid",
        "enum_unmapped",
        "schema_invalid",
        "clock_unresolvable",
        # Outbound push (P10): candidate data without an active ats_share
        # consent is SKIPPED with this class — never silently sent.
        "consent_missing",
    }
)
FIELD_POLICIES = frozenset({"ours", "theirs", "most_recent", "prefer_ours_unless_blank"})

# Engine tuning (§11.3)
BATCH_SIZE = 500
MAX_RETRIES_PER_RUN = 5
STALE_RUN_REAP_MINUTES = 10


class MappingProfile(Base):
    __tablename__ = "intg_mapping_profiles"
    __table_args__ = (Index("uq_intg_mapping_org_name", "org_id", "name", unique=True),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    # NULL = org-level reusable profile.
    connection_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("intg_connections.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    document: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    # Bumped on every document update; SyncProfiles pin a version so a live
    # sync never silently changes shape mid-run.
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SyncProfile(Base):
    __tablename__ = "intg_sync_profiles"
    __table_args__ = (
        Index("uq_intg_syncprof", "connection_id", "model", "direction", unique=True),
        Index("ix_intg_syncprof_org", "org_id", "enabled"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    connection_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_connections.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(15), nullable=False)
    mapping_profile_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("intg_mapping_profiles.id", ondelete="RESTRICT"), nullable=True
    )
    mapping_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    schedule: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    # {"<field>": "ours|theirs|most_recent|prefer_ours_unless_blank", "_default": ...}
    field_policy: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    options: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SyncRun(Base):
    __tablename__ = "intg_sync_runs"
    __table_args__ = (
        Index("ix_intg_runs_profile", "profile_id", "started_at"),
        # One live run per profile (idempotent trigger).
        Index(
            "uq_intg_run_live",
            "profile_id",
            unique=True,
            postgresql_where="status IN ('queued','running')",
        ),
    )

    id: Mapped[str] = ulid_pk()
    profile_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_sync_profiles.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    trigger: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    cursor_in: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    # Written in the SAME txn as each batch's records — destination-confirmed
    # by construction (§11.3).
    cursor_out: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    stats: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    error: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SyncRecordResult(Base):
    """Record-level observability; only non-`unchanged` outcomes get rows."""

    __tablename__ = "intg_sync_record_results"
    __table_args__ = (Index("ix_intg_recres_run", "run_id", "outcome"),)

    id: Mapped[str] = ulid_pk()
    run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_sync_runs.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    conflict_class: Mapped[str | None] = mapped_column(String(40), nullable=True)
    detail: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    resolved_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_action: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StagedRecord(Base):
    """Generic canonical staging (one table, `model` discriminator)."""

    __tablename__ = "intg_staged_records"
    __table_args__ = (
        Index("uq_intg_staged", "connection_id", "model", "external_id", unique=True),
        Index("ix_intg_staged_conn_model", "connection_id", "model", "status"),
    )

    id: Mapped[str] = ulid_pk()
    connection_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_connections.id", ondelete="CASCADE"), nullable=False
    )
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    raw_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    first_seen_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    last_seen_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # Echo suppression sidecar (§11.5): hash+time of our last outbound write.
    last_outbound: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

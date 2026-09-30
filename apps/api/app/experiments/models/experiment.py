"""Experiment core models (ADR-017 §4.1–§4.3).

Experiments carry mutable operational state (status, ramp); the versioned
specification is IMMUTABLE — `experiment_versions` rows are insert-only and
carry a canonical-JSON SHA-256 so tampering is detectable. Layers give
mutually-exclusive slice ranges so one unit never enters incompatible
experiments (contamination control, Part B).
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Total hash space per layer; buckets and slice bounds live in [0, 10000).
LAYER_TOTAL_SLICES = 10_000


class Experiment(Base):
    """One experiment: mutable operational state + pointer to immutable spec."""

    __tablename__ = "experiments"

    id: Mapped[str] = ulid_pk()
    key: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    domain: Mapped[str] = mapped_column(String(20))
    # null = platform-wide; set = org-scoped (units must belong to the org)
    scope_org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    layer_key: Mapped[str] = mapped_column(
        String(64), ForeignKey("experiment_layers.key", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(12), default="draft", server_default="draft")
    current_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    owner_user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="RESTRICT"))
    risk_class: Mapped[str] = mapped_column(String(8), default="medium", server_default="medium")
    # Percentage ramp in basis points — may only INCREASE while live (ITT)
    ramp_bp: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Per-experiment long-term holdout, basis points
    holdout_bp: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Part I: snapshots keep computing until this date (long-term outcomes)
    analysis_close_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Sweep-fairness stamp: guardrail sweeps take the oldest-checked first
    # and stamp after processing (§106.26 — caps must not starve a backlog)
    last_guardrail_check_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_experiments_status_domain", "status", "domain"),
        Index("ix_experiments_layer", "layer_key"),
        Index("ix_experiments_scope_org", "scope_org_id"),
    )


class ExperimentVersion(Base):
    """Immutable versioned specification — rows are insert-only."""

    __tablename__ = "experiment_versions"

    id: Mapped[str] = ulid_pk()
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    version: Mapped[int] = mapped_column(Integer)
    spec: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # SHA-256 over canonical JSON (sorted keys, compact separators)
    spec_hash: Mapped[str] = mapped_column(String(64))
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("experiment_id", "version", name="uq_experiment_versions_exp_version"),
    )


class ExperimentLayer(Base):
    """A mutual-exclusion universe: same-layer experiments own disjoint slices."""

    __tablename__ = "experiment_layers"

    id: Mapped[str] = ulid_pk()
    key: Mapped[str] = mapped_column(String(64), unique=True)
    domain: Mapped[str] = mapped_column(String(20))
    total_slices: Mapped[int] = mapped_column(
        Integer, default=LAYER_TOTAL_SLICES, server_default=str(LAYER_TOTAL_SLICES)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ExperimentLayerAllocation(Base):
    """Slice range [slice_start, slice_end] owned by one experiment in a layer.

    Non-overlap is enforced under SELECT ... FOR UPDATE on the layer row
    (chosen over an EXCLUDE gist constraint to avoid the btree_gist
    extension dependency — ADR-017 §4.3).
    """

    __tablename__ = "experiment_layer_allocations"

    id: Mapped[str] = ulid_pk()
    layer_key: Mapped[str] = mapped_column(
        String(64), ForeignKey("experiment_layers.key", ondelete="CASCADE")
    )
    experiment_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("experiments.id", ondelete="CASCADE")
    )
    slice_start: Mapped[int] = mapped_column(Integer)
    slice_end: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("experiment_id", name="uq_experiment_layer_allocations_experiment"),
        Index("ix_experiment_layer_allocations_layer", "layer_key"),
    )

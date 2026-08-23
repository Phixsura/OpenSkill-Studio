"""Matching engine models — requirement profiles, versioned configs, audited runs (ADR-012).

Every match run snapshots engine_version + config_version so historical
results stay explainable after ranking logic changes (Issue #21 Part H).
"""

import enum
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class RequirementContext(str, enum.Enum):
    LEARNING = "learning"
    PRODUCTION = "production"
    COMMERCIAL_PROJECT = "commercial_project"
    TALENT_MATCHING = "talent_matching"


class RequirementProfile(Base):
    """Structured representation of a user's or project's need (Issue #21 Part C)."""

    __tablename__ = "requirement_profiles"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    context_type: Mapped[RequirementContext] = mapped_column(
        Enum(RequirementContext, name="requirement_context", create_constraint=True)
    )
    # Original natural-language input — always preserved (D7)
    raw_request: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Loose ref to a ClientBrief this profile was derived from
    source_brief_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    structured_requirements: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    # {"provenance": {field: "extracted"|"user_entered"|"inferred"}, "model": ..., "unmatched_mentions": [...]}
    extraction_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_req_profiles_org", "org_id", "context_type"),)


class MatchingConfig(Base):
    """Versioned scoring weights — never mutated, only new versions (D1)."""

    __tablename__ = "matching_configs"

    id: Mapped[str] = ulid_pk()
    version: Mapped[int] = mapped_column(Integer)
    target_entity_type: Mapped[str] = mapped_column(String(30))
    # {"signal_name": weight, ...} — weights sum to 1.0
    weights: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # {"reason_min": 0.7, "gap_max": 0.4, "tier_great": 0.75, "tier_good": 0.5}
    thresholds: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("uq_matching_config", "target_entity_type", "version", unique=True),
    )


class MatchRun(Base):
    """Audited matching run (Issue #21 Part H §22)."""

    __tablename__ = "match_runs"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    context_type: Mapped[str] = mapped_column(String(30))
    requirement_profile_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("requirement_profiles.id", ondelete="SET NULL"), nullable=True
    )
    target_entity_type: Mapped[str] = mapped_column(String(30))
    engine_version: Mapped[str] = mapped_column(String(20))
    # Snapshot of the config version used (loose value, not FK — reproducibility)
    config_version: Mapped[int] = mapped_column(Integer)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    excluded_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_match_runs_org", "org_id", "created_at"),)


class MatchResult(Base):
    """One candidate's outcome in a match run — ranked OR hard-failed."""

    __tablename__ = "match_results"

    id: Mapped[str] = ulid_pk()
    match_run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("match_runs.id", ondelete="CASCADE")
    )
    entity_type: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    # NULL rank/score = hard-constraint failure (distinguishable from low rank)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    reasons: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    gaps: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    hard_failures: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Server-computed presentation tier: great | good | fair (D9)
    tier: Mapped[str | None] = mapped_column(String(20), nullable=True)

    __table_args__ = (Index("ix_matchresults_run", "match_run_id", "rank"),)


class FeedbackEvent(Base):
    """Append-only recommendation outcome log (REV-5). Never read by scoring."""

    __tablename__ = "feedback_events"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    match_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    event_type: Mapped[str] = mapped_column(String(20))
    # Position bias is unrecoverable without this (R17) — CHECK enforces it on 'shown'
    rank_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    config_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_feedback_org_entity", "org_id", "entity_type", "entity_id"),
        CheckConstraint(
            "(event_type != 'shown') OR (rank_position IS NOT NULL)",
            name="ck_feedback_rank",
        ),
    )

"""Replacement intelligence, drafts, rollout, watchlists (ADR-016 Parts J, K, M, P)."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

REPLACEMENT_EDGE_TYPES = frozenset(
    {"supersedes", "recommended_replacement", "compatible_alternative", "migration_required"}
)

CANDIDATE_STATUSES = frozenset({"proposed", "under_review", "approved", "rejected"})

# Default replacement scoring weights (sum to 1.0; ADR-016 §3.9)
DEFAULT_REPLACEMENT_WEIGHTS = {
    "io": 0.2,
    "capability": 0.15,
    "benchmark": 0.15,
    "reliability": 0.15,
    "cost": 0.10,
    "latency": 0.05,
    "license": 0.05,
    "availability": 0.05,
    "bindings": 0.05,
    "migration": 0.05,
}

DRAFT_TYPES = frozenset(
    {
        "workflow_pack",
        "skill_pack_update",
        "project_template",
        "capability_mapping",
        "provider_offering",
        "benchmark_suite",
    }
)

DRAFT_STATUSES = frozenset({"draft", "in_review", "approved", "rejected", "published"})

ROLLOUT_SCOPES = frozenset(
    {"benchmark_only", "internal_org", "selected_cohort", "selected_installation"}
)

ROLLOUT_STATUSES = frozenset(
    {"draft", "running", "evaluating", "promoted", "rejected", "aborted"}
)

WATCH_TARGET_KINDS = frozenset(
    {
        "provider", "model", "model_version", "tool", "workflow", "agent",
        "node_package", "github_repo", "capability", "component",
    }
)


class ReplacementEdge(Base):
    """Directed replacement relationship between two entities/components."""

    __tablename__ = "eco_replacement_edges"

    id: Mapped[str] = ulid_pk()
    from_kind: Mapped[str] = mapped_column(String(40))
    from_id: Mapped[str] = mapped_column(String(26))
    to_kind: Mapped[str] = mapped_column(String(40))
    to_id: Mapped[str] = mapped_column(String(26))
    # supersedes | recommended_replacement | compatible_alternative | migration_required
    edge_type: Mapped[str] = mapped_column(String(40))
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "from_kind", "from_id", "to_kind", "to_id", "edge_type", name="uq_eco_repl_edge"
        ),
        Index("ix_eco_repl_from", "from_kind", "from_id"),
    )


class ReplacementCandidate(Base):
    """A scored, explainable replacement suggestion. Human-confirmed only.

    Hard rule: hard_compatible=false rows are NEVER interleaved into ranked
    results regardless of score (ADR-016 §3.9).
    """

    __tablename__ = "eco_replacement_candidates"

    id: Mapped[str] = ulid_pk()
    deprecated_kind: Mapped[str] = mapped_column(String(40))
    deprecated_id: Mapped[str] = mapped_column(String(26))
    candidate_kind: Mapped[str] = mapped_column(String(40))
    candidate_id: Mapped[str] = mapped_column(String(26))
    score: Mapped[float] = mapped_column(Numeric(5, 4), default=0)
    hard_compatible: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    # [{"code": "IO_TYPE_MISMATCH", "detail": "..."}]
    hard_failures: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Per-factor scores (io, capability, benchmark, reliability, cost, latency,
    # license, availability, bindings, migration)
    score_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Human-readable factor lines, mirrors ADR-012 explain contract
    explanation: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # proposed | under_review | approved | rejected
    status: Mapped[str] = mapped_column(String(20), default="proposed", server_default="proposed")
    decided_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_eco_candidates_deprecated", "deprecated_kind", "deprecated_id", "status"),
    )


class ComponentDraft(Base):
    """DRAFT-only artifact generated from verified external intelligence.

    Publishing requires status=approved plus an explicit second human action —
    the service refuses draft→published in one step (ECO_DRAFT_NOT_APPROVED).
    """

    __tablename__ = "eco_component_drafts"

    id: Mapped[str] = ulid_pk()
    # workflow_pack | skill_pack_update | project_template | capability_mapping |
    # provider_offering | benchmark_suite
    draft_type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(300))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    source_kind: Mapped[str | None] = mapped_column(String(40), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    source_observation_ids: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # {"valid": true, "errors": []}
    validation: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # draft | in_review | approved | rejected | published
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Id of the created product entity after publish
    published_ref: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_eco_drafts_status", "draft_type", "status"),)


class RolloutPlan(Base):
    """Controlled rollout/canary validation of a replacement candidate (Part M).

    Promote/reject are explicit human POST actions; no automatic promotion
    path exists, and promotion never rewrites existing step bindings.
    """

    __tablename__ = "eco_rollout_plans"

    id: Mapped[str] = ulid_pk()
    replacement_candidate_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_replacement_candidates.id", ondelete="RESTRICT")
    )
    # benchmark_only | internal_org | selected_cohort | selected_installation
    scope_type: Mapped[str] = mapped_column(String(30))
    scope_ref: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # §11.4 guardrails: {"min_samples": int, "thresholds": {dim: max_regression}}
    guardrails: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Metrics snapshot of the incumbent at plan creation
    baseline: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    candidate_metrics: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Per-dimension deltas: {"cost": -0.35, "quality": +0.02, ...}
    comparison: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # draft | running | evaluating | promoted | rejected | aborted
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    decided_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_eco_rollouts_status", "status"),)


class Watchlist(Base):
    """A user's named watchlist (Part P)."""

    __tablename__ = "eco_watchlists"

    id: Mapped[str] = ulid_pk()
    owner_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200))
    # Renovate-style noise controls: only changes at/above this severity
    # notify; muted_until snoozes push notifications entirely (pull unaffected)
    min_severity: Mapped[str] = mapped_column(String(30), default="info", server_default="info")
    muted_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_eco_watchlists_owner", "owner_id"),)


class WatchItem(Base):
    """One watched target inside a watchlist."""

    __tablename__ = "eco_watch_items"

    id: Mapped[str] = ulid_pk()
    watchlist_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_watchlists.id", ondelete="CASCADE")
    )
    # provider | model | tool | workflow | github_repo | capability | component
    target_kind: Mapped[str] = mapped_column(String(30))
    # For catalog/component targets
    target_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # For external references (repo URLs etc.)
    target_ref: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_eco_watch_items_list", "watchlist_id"),)

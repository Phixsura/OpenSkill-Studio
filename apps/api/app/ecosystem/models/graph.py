"""Dependency graph, impact analysis, telemetry evidence (ADR-016 Parts G, H, I)."""

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

# Node kinds span external catalog + product components
GRAPH_NODE_KINDS = frozenset(
    {
        "provider",
        "model",
        "model_version",
        "tool",
        "node_package",
        "workflow",
        "agent",
        "workflow_pack",
        "workflow_pack_release",
        "skill_pack",
        "project_template",
        "learning_path",
        "assessment",
        "capability",
        "commercial_project",
        "cohort",
    }
)

CONSTRAINT_TYPES = frozenset(
    {
        "requires_model_version",
        "requires_capability",
        "requires_api_version",
        "requires_node_package",
        "requires_license",
        "requires_runtime_feature",
        "uses",
    }
)

IMPACT_CLASSIFICATIONS = frozenset(
    {
        "informational",
        "update_available",
        "degraded",
        "breaking",
        "security_critical",
        "sunset_risk",
    }
)

RECOMMENDED_ACTIONS = frozenset({"none", "review", "update", "migrate", "block"})

# BFS traversal caps (cycle-safe; ADR-016 §3.8)
IMPACT_MAX_DEPTH = 6
IMPACT_MAX_NODES = 5000

# Privacy thresholds for cross-tenant telemetry aggregates (ADR-016 §3.7)
TELEMETRY_MIN_SAMPLE = 20
TELEMETRY_MIN_ORGS = 3


class DependencyEdge(Base):
    """Typed dependency edge: from-component depends on to-component."""

    __tablename__ = "eco_dependency_edges"

    id: Mapped[str] = ulid_pk()
    from_kind: Mapped[str] = mapped_column(String(40))
    from_id: Mapped[str] = mapped_column(String(26))
    to_kind: Mapped[str] = mapped_column(String(40))
    to_id: Mapped[str] = mapped_column(String(26))
    constraint_type: Mapped[str] = mapped_column(String(40), default="uses", server_default="uses")
    # {"version_range": ">=2.0 <3.0"} / {"license": "commercial"} ...
    constraint_spec: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Private component edges are org-scoped; NULL = platform-visible
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "from_kind", "from_id", "to_kind", "to_id", "constraint_type", name="uq_eco_dep_edge"
        ),
        Index("ix_eco_dep_to", "to_kind", "to_id"),
        Index("ix_eco_dep_from", "from_kind", "from_id"),
    )


class ImpactAnalysis(Base):
    """Stored transitive impact computation for one change event."""

    __tablename__ = "eco_impact_analyses"

    id: Mapped[str] = ulid_pk()
    change_event_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_change_events.id", ondelete="CASCADE")
    )
    root_kind: Mapped[str] = mapped_column(String(40))
    root_id: Mapped[str] = mapped_column(String(26))
    # informational | update_available | degraded | breaking |
    # security_critical | sunset_risk
    classification: Mapped[str] = mapped_column(String(30))
    # {"workflow_pack": 12, "learning_path": 4, "cohort": 8, "truncated": false}
    summary: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # open | acknowledged | resolved
    status: Mapped[str] = mapped_column(String(20), default="open", server_default="open")

    __table_args__ = (
        Index("ix_eco_impact_root", "root_kind", "root_id"),
        Index("ix_eco_impact_status", "status", "classification"),
    )


class ImpactItem(Base):
    """One affected component in an impact analysis."""

    __tablename__ = "eco_impact_items"

    id: Mapped[str] = ulid_pk()
    analysis_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_impact_analyses.id", ondelete="CASCADE")
    )
    node_kind: Mapped[str] = mapped_column(String(40))
    node_id: Mapped[str] = mapped_column(String(26))
    depth: Mapped[int] = mapped_column(Integer, default=1)
    # Edge-id path from root for explainability
    path: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # {"active_cohorts": 3, "running_projects": 1}
    active_usage: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # none | review | update | migrate | block
    recommended_action: Mapped[str] = mapped_column(
        String(40), default="review", server_default="review"
    )

    __table_args__ = (Index("ix_eco_impact_items_analysis", "analysis_id"),)


class TelemetrySnapshot(Base):
    """Privacy-safe production evidence aggregate (Part G).

    org_id NULL means cross-tenant aggregate — only written when
    sample_size >= TELEMETRY_MIN_SAMPLE and >= TELEMETRY_MIN_ORGS orgs
    contributed.
    """

    __tablename__ = "eco_telemetry_snapshots"

    id: Mapped[str] = ulid_pk()
    entity_kind: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    # {"success_rate":..., "retry_rate":..., "latency_p50_ms":..., "latency_p95_ms":...,
    #  "effective_cost_usd_avg":..., "human_approval_rate":..., "revision_rate":...,
    #  "client_acceptance_rate":..., "error_distribution": {...}}
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "entity_kind",
            "entity_id",
            "org_id",
            "window_start",
            "window_end",
            name="uq_eco_telemetry_window",
        ),
        Index("ix_eco_telemetry_entity", "entity_kind", "entity_id", "window_end"),
    )

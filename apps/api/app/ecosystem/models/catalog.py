"""Canonical AI ecosystem catalog + entity resolution (ADR-016 Part C, L).

Multiple observations resolve to one canonical entity. Resolution uses
official IDs and deterministic aliases first, then similarity; LLM-suggested
or low-confidence merges are queued for human confirmation.
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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Part L lifecycle states for external capabilities
LIFECYCLE_STATUSES = frozenset(
    {
        "discovered",
        "under_review",
        "verified",
        "recommended",
        "watch",
        "deprecated",
        "blocked",
        "retired",
    }
)

# Valid lifecycle transitions (service-enforced; ADR-016 §3.9)
LIFECYCLE_TRANSITIONS: dict[str, frozenset[str]] = {
    "discovered": frozenset({"under_review", "blocked"}),
    "under_review": frozenset({"verified", "blocked", "discovered"}),
    "verified": frozenset({"recommended", "watch", "deprecated", "blocked"}),
    "recommended": frozenset({"watch", "deprecated", "blocked"}),
    "watch": frozenset({"recommended", "deprecated", "blocked"}),
    "deprecated": frozenset({"retired", "watch"}),
    "blocked": frozenset({"under_review", "retired"}),
    "retired": frozenset(),
}

DEPRECATION_REASONS = frozenset(
    {
        "official_sunset",
        "security_advisory",
        "license_incompatibility",
        "benchmark_regression",
        "production_failure_threshold",
        "manual_decision",
    }
)

RESOLUTION_METHODS = frozenset({"official_id", "alias", "similarity", "llm_suggested"})

# Auto-merge policy: only deterministic methods at high confidence may merge
# without a human (ADR-016 §3.3)
AUTO_MERGE_METHODS = frozenset({"official_id", "alias"})
AUTO_MERGE_MIN_CONFIDENCE = 0.9


def _canonical_columns(cls: type) -> None:  # pragma: no cover - declarative helper doc
    """Shared column core documented in ADR-016 §3.3 (applied per-class below)."""


class AIProvider(Base):
    """Canonical external AI provider (vendor)."""

    __tablename__ = "eco_ai_providers"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="discovered", server_default="discovered"
    )
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # operational | degraded | outage | unknown
    vendor_status: Mapped[str] = mapped_column(
        String(20), default="unknown", server_default="unknown"
    )
    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_eco_providers_lifecycle", "lifecycle_status"),)


class AITool(Base):
    """Canonical external AI tool (API service, desktop app, CLI, node...)."""

    __tablename__ = "eco_ai_tools"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="discovered", server_default="discovered"
    )
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    provider_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_ai_providers.id", ondelete="SET NULL"), nullable=True
    )
    # api | desktop | node | cli | service
    tool_type: Mapped[str] = mapped_column(String(20), default="api", server_default="api")
    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_eco_tools_lifecycle", "lifecycle_status"),)


class AIModel(Base):
    """Canonical external AI model family (versions live in eco_model_versions)."""

    __tablename__ = "eco_ai_models"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="discovered", server_default="discovered"
    )
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    provider_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_ai_providers.id", ondelete="SET NULL"), nullable=True
    )
    # {"inputs": ["text", "image"], "outputs": ["video"]}
    modalities: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_eco_models_lifecycle", "lifecycle_status"),
        Index("ix_eco_models_provider", "provider_id"),
    )


class ModelVersion(Base):
    """A specific released version of a canonical AI model."""

    __tablename__ = "eco_model_versions"

    id: Mapped[str] = ulid_pk()
    model_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_ai_models.id", ondelete="CASCADE")
    )
    version: Mapped[str] = mapped_column(String(100))
    canonical_name: Mapped[str] = mapped_column(String(200))
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="discovered", server_default="discovered"
    )
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deprecated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sunset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # The identifier used when calling the provider API
    api_identifier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # {"max_input_mp": 25, "max_output_seconds": 10, "context_tokens": 200000, ...}
    limits: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    license: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commercial_use_allowed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("model_id", "version", name="uq_eco_model_version"),
        Index("ix_eco_model_versions_lifecycle", "lifecycle_status"),
        Index("ix_eco_model_versions_sunset", "sunset_at"),
    )


class ExternalWorkflow(Base):
    """A community/external workflow definition (e.g. a ComfyUI graph)."""

    __tablename__ = "eco_external_workflows"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="discovered", server_default="discovered"
    )
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    source_repo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # comfyui | other
    workflow_format: Mapped[str] = mapped_column(
        String(20), default="comfyui", server_default="comfyui"
    )
    node_types: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    graph_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_eco_ext_workflows_lifecycle", "lifecycle_status"),)


class ExternalAgent(Base):
    """A canonical external agent (framework-hosted autonomous component)."""

    __tablename__ = "eco_external_agents"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="discovered", server_default="discovered"
    )
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    agent_framework: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExternalNodePackage(Base):
    """A canonical external node/plugin package (e.g. ComfyUI custom nodes)."""

    __tablename__ = "eco_node_packages"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="discovered", server_default="discovered"
    )
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    package_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    repo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latest_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # [{"advisory": "GHSA-...", "severity": "high"}]
    security_flags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# Table name lookup for the generic (entity_kind, entity_id) loose references
CATALOG_KIND_TO_MODEL = {
    "provider": AIProvider,
    "tool": AITool,
    "model": AIModel,
    "model_version": ModelVersion,
    "workflow": ExternalWorkflow,
    "agent": ExternalAgent,
    "node_package": ExternalNodePackage,
}


class EntityAlias(Base):
    """Deterministic alias registry for entity resolution."""

    __tablename__ = "eco_entity_aliases"

    id: Mapped[str] = ulid_pk()
    entity_kind: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    alias: Mapped[str] = mapped_column(String(300))
    # official_id | slug | name | api_identifier
    alias_type: Mapped[str] = mapped_column(String(30), default="name", server_default="name")
    source_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_sources.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("entity_kind", "alias", "alias_type", name="uq_eco_alias"),
        Index("ix_eco_aliases_entity", "entity_kind", "entity_id"),
    )


class ResolutionCandidate(Base):
    """Queued entity-resolution decision (auto-merged or awaiting a human)."""

    __tablename__ = "eco_resolution_candidates"

    id: Mapped[str] = ulid_pk()
    observation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("eco_observations.id", ondelete="CASCADE")
    )
    entity_kind: Mapped[str] = mapped_column(String(30))
    # NULL proposes creating a NEW canonical entity
    candidate_entity_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # official_id | alias | similarity | llm_suggested
    match_method: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=0.0)
    proposed_payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # pending | auto_merged | confirmed | rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    decided_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_eco_resolution_status", "status"),
        Index("ix_eco_resolution_obs", "observation_id"),
    )


class LifecycleTransition(Base):
    """Audit log of lifecycle state changes on canonical entities (Part L)."""

    __tablename__ = "eco_lifecycle_transitions"

    id: Mapped[str] = ulid_pk()
    entity_kind: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(26))
    from_status: Mapped[str] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20))
    # official_sunset | security_advisory | license_incompatibility |
    # benchmark_regression | production_failure_threshold | manual_decision
    reason: Mapped[str | None] = mapped_column(String(40), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_eco_lifecycle_entity", "entity_kind", "entity_id", "created_at"),)

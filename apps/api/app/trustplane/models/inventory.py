"""AI System Inventory models (ADR-017 Part A).

Canonical records for every governed AI capability — workflow packs,
developer apps, provider bindings, evaluation pipelines, etc.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class SystemType(str, enum.Enum):
    WORKFLOW_PACK = "workflow_pack"
    DEVELOPER_APP = "developer_app"
    PROVIDER_BINDING = "provider_binding"
    EVALUATION_PIPELINE = "evaluation_pipeline"
    SKILL_PACK = "skill_pack"
    CUSTOM = "custom"


class SystemLifecycle(str, enum.Enum):
    DRAFT = "draft"
    INTAKE = "intake"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    MONITORING = "monitoring"
    PAUSED = "paused"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class RiskTier(str, enum.Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UseType(str, enum.Enum):
    INTENDED = "intended"
    PROHIBITED = "prohibited"


# ── Lifecycle transition map ─────────────────────────────────────────

VALID_TRANSITIONS: dict[SystemLifecycle, set[SystemLifecycle]] = {
    SystemLifecycle.DRAFT: {SystemLifecycle.INTAKE},
    SystemLifecycle.INTAKE: {SystemLifecycle.UNDER_REVIEW, SystemLifecycle.DRAFT},
    SystemLifecycle.UNDER_REVIEW: {SystemLifecycle.APPROVED, SystemLifecycle.INTAKE},
    SystemLifecycle.APPROVED: {SystemLifecycle.DEPLOYED, SystemLifecycle.PAUSED},
    SystemLifecycle.DEPLOYED: {
        SystemLifecycle.MONITORING,
        SystemLifecycle.PAUSED,
        SystemLifecycle.DEPRECATED,
    },
    SystemLifecycle.MONITORING: {SystemLifecycle.PAUSED, SystemLifecycle.DEPRECATED},
    SystemLifecycle.PAUSED: {
        SystemLifecycle.DEPLOYED,
        SystemLifecycle.MONITORING,
        SystemLifecycle.DEPRECATED,
        SystemLifecycle.RETIRED,
    },
    SystemLifecycle.DEPRECATED: {SystemLifecycle.RETIRED, SystemLifecycle.PAUSED},
    SystemLifecycle.RETIRED: set(),  # terminal
}


# ── Models ───────────────────────────────────────────────────────────


class AISystem(Base):
    __tablename__ = "trust_ai_systems"
    __table_args__ = (
        Index("uq_trust_system_org_slug", "org_id", "slug", unique=True),
        Index("ix_trust_system_org_lifecycle", "org_id", "lifecycle"),
        Index("ix_trust_system_org_type", "org_id", "system_type"),
        Index("ix_trust_system_org_risk", "org_id", "risk_tier"),
        Index("ix_trust_system_linked", "linked_entity_type", "linked_entity_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_type: Mapped[SystemType] = mapped_column(
        Enum(SystemType, name="trust_system_type", create_constraint=True), nullable=False
    )
    lifecycle: Mapped[SystemLifecycle] = mapped_column(
        Enum(SystemLifecycle, name="trust_system_lifecycle", create_constraint=True),
        nullable=False,
        default=SystemLifecycle.DRAFT,
    )
    risk_tier: Mapped[RiskTier | None] = mapped_column(
        Enum(RiskTier, name="trust_risk_tier", create_constraint=True), nullable=True
    )
    owner_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    # Loose coupling — linked entity may be deleted independently
    linked_entity_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    linked_entity_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict, server_default="{}"
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AISystemUseCase(Base):
    __tablename__ = "trust_ai_system_uses"
    __table_args__ = (Index("ix_trust_use_system_type", "system_id", "use_type"),)

    id: Mapped[str] = ulid_pk()
    system_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False
    )
    use_type: Mapped[UseType] = mapped_column(
        Enum(UseType, name="trust_use_type", create_constraint=True), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_groups: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    data_classes: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    deployment_contexts: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    regions: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

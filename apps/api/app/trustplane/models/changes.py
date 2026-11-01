"""Change Management & Revalidation models (ADR-017 Part K).

Tracks assurance-changing events (model versions, prompts, tools,
dependencies, data sources, evaluation methods) and triggers impact
analysis to determine which evidence remains valid.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class ChangeType(str, enum.Enum):
    MODEL_VERSION = "model_version"
    PROVIDER_VERSION = "provider_version"
    PROMPT_TEMPLATE = "prompt_template"
    TOOL_PERMISSION = "tool_permission"
    COMPONENT_DEPENDENCY = "component_dependency"
    DATA_SOURCE = "data_source"
    EVALUATION_METHOD = "evaluation_method"
    INTENDED_USE = "intended_use"
    DEPLOYMENT_SCALE = "deployment_scale"
    CONFIGURATION = "configuration"


class ChangeImpact(str, enum.Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    REQUIRES_REVALIDATION = "requires_revalidation"


class RevalidationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ── Models ───────────────────────────────────────────────────────────


class ChangeEvent(Base):
    """Record of an assurance-changing event."""

    __tablename__ = "trust_change_events"
    __table_args__ = (
        Index("ix_trust_change_org", "org_id", "created_at"),
        Index("ix_trust_change_system", "system_id"),
        Index("ix_trust_change_type", "change_type"),
        Index("ix_trust_change_impact", "impact"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False
    )
    change_type: Mapped[ChangeType] = mapped_column(
        Enum(ChangeType, name="trust_change_type", create_constraint=True), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # What changed
    before_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Impact analysis
    impact: Mapped[ChangeImpact] = mapped_column(
        Enum(ChangeImpact, name="trust_change_impact", create_constraint=True),
        nullable=False,
        default=ChangeImpact.LOW,
    )
    affected_evidence: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )  # evidence IDs that need revalidation
    affected_assessments: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    # Revalidation
    requires_revalidation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    revalidation_status: Mapped[RevalidationStatus] = mapped_column(
        Enum(RevalidationStatus, name="trust_revalidation_status", create_constraint=True),
        nullable=False,
        default=RevalidationStatus.PENDING,
    )
    revalidated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revalidated_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Source
    detected_by: Mapped[str] = mapped_column(
        String(20), nullable=False, default="manual"
    )  # manual | system | webhook
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

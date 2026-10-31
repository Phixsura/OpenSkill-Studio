"""Runtime Guardrails & Action Boundaries models (ADR-017 Part F).

Server-side guardrail policies that cannot be disabled by model output,
prompts, or extension manifests. Records policy version and reason for
every blocked or escalated action.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
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


class GuardrailType(str, enum.Enum):
    TOOL_ALLOWLIST = "tool_allowlist"
    PERMISSION_BOUNDARY = "permission_boundary"
    DATA_LOSS_PREVENTION = "data_loss_prevention"
    EGRESS_RESTRICTION = "egress_restriction"
    OUTPUT_SCHEMA = "output_schema"
    ACTION_BUDGET = "action_budget"
    RATE_LIMIT = "rate_limit"
    SPEND_CEILING = "spend_ceiling"
    HUMAN_CONFIRMATION = "human_confirmation"
    CONTENT_FILTER = "content_filter"


class GuardrailStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"


class EvalVerdict(str, enum.Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"
    RATE_LIMITED = "rate_limited"


# ── Models ───────────────────────────────────────────────────────────


class GuardrailPolicy(Base):
    """A server-side guardrail policy applied to AI system execution."""

    __tablename__ = "trust_guardrail_policies"
    __table_args__ = (
        Index("ix_trust_guardrail_org_type", "org_id", "guardrail_type"),
        Index("ix_trust_guardrail_system", "system_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True
    )  # NULL = org-wide policy
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    guardrail_type: Mapped[GuardrailType] = mapped_column(
        Enum(GuardrailType, name="trust_guardrail_type", create_constraint=True), nullable=False
    )
    status: Mapped[GuardrailStatus] = mapped_column(
        Enum(GuardrailStatus, name="trust_guardrail_status", create_constraint=True),
        nullable=False,
        default=GuardrailStatus.DRAFT,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    # Policy configuration — shape depends on guardrail_type
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_blocking: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )  # if False, logs only (shadow mode)
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100
    )  # lower = evaluated first
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GuardrailEvaluation(Base):
    """Per-execution guardrail check log — append-only."""

    __tablename__ = "trust_guardrail_evaluations"
    __table_args__ = (
        Index("ix_trust_geval_org_created", "org_id", "created_at"),
        Index("ix_trust_geval_policy", "policy_id"),
        Index("ix_trust_geval_verdict", "verdict"),
        Index("ix_trust_geval_run", "run_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    policy_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_guardrail_policies.id", ondelete="SET NULL"), nullable=False
    )
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    # What triggered the evaluation
    run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # workflow_run id
    step_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    system_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # Result
    verdict: Mapped[EvalVerdict] = mapped_column(
        Enum(EvalVerdict, name="trust_eval_verdict", create_constraint=True), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    input_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ActionBoundary(Base):
    """Spend ceilings, rate limits, and action budgets per system or org."""

    __tablename__ = "trust_action_boundaries"
    __table_args__ = (
        Index("ix_trust_boundary_org", "org_id"),
        Index("ix_trust_boundary_system", "system_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True
    )  # NULL = org-wide
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    boundary_type: Mapped[str] = mapped_column(
        String(40), nullable=False
    )  # spend_ceiling, action_budget, rate_limit
    # Limits
    limit_value: Mapped[int] = mapped_column(Integer, nullable=False)
    limit_period: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # hour, day, week, month, or NULL for absolute
    current_usage: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

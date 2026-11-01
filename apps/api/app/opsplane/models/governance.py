"""Policy, FinOps, Compliance, Change Management & Self-healing models (ADR-018 Parts G, H, J, K, M, N, O, P, R, S).

Policy-as-code, remediation playbooks, AI FinOps, capacity planning,
compliance evidence, data retention, change management, governance
approvals, game days, and human-supervised self-healing.
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
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


class PolicyStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class PlaybookStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class PlaybookRunStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class CostCategory(str, enum.Enum):
    COMPUTE = "compute"
    AI_INFERENCE = "ai_inference"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    THIRD_PARTY = "third_party"
    LICENSING = "licensing"


class GameDayStatus(str, enum.Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HealingActionStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


# ── Models ───────────────────────────────────────────────────────────


class OpsPolicy(Base):
    """Policy-as-code rule (Part G)."""

    __tablename__ = "ops_policies"
    __table_args__ = (
        Index("ix_ops_policy_type", "policy_type"),
        Index("ix_ops_policy_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    policy_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus, name="ops_policy_status", create_constraint=True),
        nullable=False, default=PolicyStatus.DRAFT,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    rules: Mapped[dict] = mapped_column(JSONB, nullable=False)
    enforcement_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="enforce")
    scope: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RemediationPlaybook(Base):
    """Safe remediation playbook (Part H)."""

    __tablename__ = "ops_remediation_playbooks"
    __table_args__ = (
        Index("ix_ops_playbook_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    steps: Mapped[list] = mapped_column(JSONB, nullable=False)
    rollback_steps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    blast_radius_check: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[PlaybookStatus] = mapped_column(
        Enum(PlaybookStatus, name="ops_playbook_status", create_constraint=True),
        nullable=False, default=PlaybookStatus.DRAFT,
    )
    max_concurrent: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PlaybookRun(Base):
    """Execution record of a remediation playbook."""

    __tablename__ = "ops_playbook_runs"
    __table_args__ = (
        Index("ix_ops_pbrun_playbook", "playbook_id"),
        Index("ix_ops_pbrun_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    playbook_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("ops_remediation_playbooks.id", ondelete="CASCADE"), nullable=False
    )
    incident_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    status: Mapped[PlaybookRunStatus] = mapped_column(
        Enum(PlaybookRunStatus, name="ops_playbook_run_status", create_constraint=True),
        nullable=False, default=PlaybookRunStatus.PENDING_APPROVAL,
    )
    step_results: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    approved_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    executed_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CostRecord(Base):
    """AI FinOps cost tracking (Part J)."""

    __tablename__ = "ops_cost_records"
    __table_args__ = (
        Index("ix_ops_cost_category", "category"),
        Index("ix_ops_cost_period", "period_start", "period_end"),
        Index("ix_ops_cost_tenant", "tenant_id"),
    )

    id: Mapped[str] = ulid_pk()
    tenant_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # NULL = platform
    category: Mapped[CostCategory] = mapped_column(
        Enum(CostCategory, name="ops_cost_category", create_constraint=True), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    region_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)  # in minor units
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # requests, tokens, gb_hours
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tags: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CostBudget(Base):
    """Cost budget with alerts (Part J)."""

    __tablename__ = "ops_cost_budgets"
    __table_args__ = (
        Index("ix_ops_budget_tenant", "tenant_id"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tenant_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    budget_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    period: Mapped[str] = mapped_column(String(20), nullable=False, default="monthly")
    current_spend_minor: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    alert_thresholds: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[50, 80, 100]")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CapacityForecast(Base):
    """Capacity planning forecast (Part K)."""

    __tablename__ = "ops_capacity_forecasts"
    __table_args__ = (
        Index("ix_ops_capacity_region", "region_id"),
    )

    id: Mapped[str] = ulid_pk()
    region_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)  # compute, storage, inference
    current_usage: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    projected_usage: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    capacity_limit: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    forecast_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    recommendations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ComplianceEvidence(Base):
    """Compliance evidence snapshot (Part M)."""

    __tablename__ = "ops_compliance_evidence"
    __table_args__ = (
        Index("ix_ops_compliance_framework", "framework"),
    )

    id: Mapped[str] = ulid_pk()
    framework: Mapped[str] = mapped_column(String(60), nullable=False)  # SOC2, GDPR, ISO27001
    control_id: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="collected")
    evidence_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RetentionPolicy(Base):
    """Data retention / deletion orchestration (Part N)."""

    __tablename__ = "ops_retention_policies"

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    data_category: Mapped[str] = mapped_column(String(60), nullable=False)
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False)
    deletion_strategy: Mapped[str] = mapped_column(String(40), nullable=False, default="soft_delete")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OpsChangeRecord(Base):
    """Change management record (Part O)."""

    __tablename__ = "ops_change_records"
    __table_args__ = (
        Index("ix_ops_change_status", "status"),
        Index("ix_ops_change_created", "created_at"),
    )

    id: Mapped[str] = ulid_pk()
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_type: Mapped[str] = mapped_column(String(40), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="proposed")
    affected_services: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    rollback_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    executed_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GovernanceApproval(Base):
    """Governance approval record (Part P)."""

    __tablename__ = "ops_governance_approvals"
    __table_args__ = (
        Index("ix_ops_approval_target", "target_type", "target_id"),
        Index("ix_ops_approval_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[str] = mapped_column(String(26), nullable=False)
    approval_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    requested_by: Mapped[str] = mapped_column(String(26), nullable=False)
    decided_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GameDay(Base):
    """Game day / chaos testing (Part R)."""

    __tablename__ = "ops_game_days"

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scenario: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[GameDayStatus] = mapped_column(
        Enum(GameDayStatus, name="ops_game_day_status", create_constraint=True),
        nullable=False, default=GameDayStatus.PLANNED,
    )
    plan: Mapped[dict] = mapped_column(JSONB, nullable=False)
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    participants: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class HealingAction(Base):
    """Human-supervised self-healing action (Part S)."""

    __tablename__ = "ops_healing_actions"
    __table_args__ = (
        Index("ix_ops_healing_status", "status"),
        Index("ix_ops_healing_incident", "incident_id"),
    )

    id: Mapped[str] = ulid_pk()
    incident_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    detection_rule_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    playbook_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    action_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[HealingActionStatus] = mapped_column(
        Enum(HealingActionStatus, name="ops_healing_action_status", create_constraint=True),
        nullable=False, default=HealingActionStatus.PROPOSED,
    )
    blast_radius: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    approved_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

"""SLO, Incidents, Failover & Recovery models (ADR-018 Parts C, E, F, I, L).

Error budgets, incident lifecycle, automated detection, provider failover,
and disaster recovery.
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
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


class SloStatus(str, enum.Enum):
    MET = "met"
    AT_RISK = "at_risk"
    BREACHED = "breached"
    PAUSED = "paused"


class OpsIncidentSeverity(str, enum.Enum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"


class OpsIncidentStatus(str, enum.Enum):
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    POST_MORTEM = "post_mortem"
    CLOSED = "closed"


class FailoverStatus(str, enum.Enum):
    IDLE = "idle"
    TRIGGERED = "triggered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class RecoveryPlanStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    TESTED = "tested"
    DEPRECATED = "deprecated"


class DetectionRuleStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    TESTING = "testing"


# ── Models ───────────────────────────────────────────────────────────


class SloDefinition(Base):
    __tablename__ = "ops_slo_definitions"
    __table_args__ = (
        Index("ix_ops_slo_org", "org_id"),
        Index("ix_ops_slo_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # NULL = platform-wide
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sli_metric: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. availability, latency_p99
    target_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)  # e.g. 99.9
    target_unit: Mapped[str] = mapped_column(String(20), nullable=False)  # percent, milliseconds
    window_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    error_budget_total: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    error_budget_remaining: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    status: Mapped[SloStatus] = mapped_column(
        Enum(SloStatus, name="ops_slo_status", create_constraint=True),
        nullable=False, default=SloStatus.MET,
    )
    alert_thresholds: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OpsIncident(Base):
    __tablename__ = "ops_incidents"
    __table_args__ = (
        Index("ix_ops_incident_severity", "severity"),
        Index("ix_ops_incident_status", "status"),
        Index("ix_ops_incident_region", "region_id"),
    )

    id: Mapped[str] = ulid_pk()
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[OpsIncidentSeverity] = mapped_column(
        Enum(OpsIncidentSeverity, name="ops_incident_severity", create_constraint=True), nullable=False
    )
    status: Mapped[OpsIncidentStatus] = mapped_column(
        Enum(OpsIncidentStatus, name="ops_incident_status", create_constraint=True),
        nullable=False, default=OpsIncidentStatus.DETECTED,
    )
    region_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    affected_services: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    affected_tenants: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    detection_source: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    slo_impact: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DetectionRule(Base):
    __tablename__ = "ops_detection_rules"
    __table_args__ = (
        Index("ix_ops_detection_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(String(40), nullable=False)  # threshold, anomaly, composite
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    severity: Mapped[OpsIncidentSeverity] = mapped_column(
        Enum(OpsIncidentSeverity, name="ops_incident_severity", create_constraint=False), nullable=False
    )
    status: Mapped[DetectionRuleStatus] = mapped_column(
        Enum(DetectionRuleStatus, name="ops_detection_rule_status", create_constraint=True),
        nullable=False, default=DetectionRuleStatus.ACTIVE,
    )
    cooldown_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FailoverRecord(Base):
    __tablename__ = "ops_failover_records"
    __table_args__ = (
        Index("ix_ops_failover_status", "status"),
        Index("ix_ops_failover_created", "created_at"),
    )

    id: Mapped[str] = ulid_pk()
    source_region_id: Mapped[str] = mapped_column(String(26), nullable=False)
    target_region_id: Mapped[str] = mapped_column(String(26), nullable=False)
    trigger: Mapped[str] = mapped_column(String(40), nullable=False)  # manual, automated, detection_rule
    incident_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    status: Mapped[FailoverStatus] = mapped_column(
        Enum(FailoverStatus, name="ops_failover_status", create_constraint=True),
        nullable=False, default=FailoverStatus.TRIGGERED,
    )
    services_migrated: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    tenants_migrated: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    initiated_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RecoveryPlan(Base):
    __tablename__ = "ops_recovery_plans"
    __table_args__ = (
        Index("ix_ops_recovery_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scenario: Mapped[str] = mapped_column(String(100), nullable=False)  # region_loss, db_failure, provider_outage
    status: Mapped[RecoveryPlanStatus] = mapped_column(
        Enum(RecoveryPlanStatus, name="ops_recovery_plan_status", create_constraint=True),
        nullable=False, default=RecoveryPlanStatus.DRAFT,
    )
    steps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    rto_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rpo_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    test_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

"""Continuous Monitoring & Drift Detection models (ADR-017 Part I).

Configured monitors per system with thresholds, alert routing, and
incident linkage. Supports quality/safety regression, behavior drift,
guardrail rates, cost anomalies, and expired evidence detection.
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


class MonitorType(str, enum.Enum):
    QUALITY_REGRESSION = "quality_regression"
    SAFETY_REGRESSION = "safety_regression"
    BEHAVIOR_DRIFT = "behavior_drift"
    GUARDRAIL_RATE = "guardrail_rate"
    COST_ANOMALY = "cost_anomaly"
    LATENCY_ANOMALY = "latency_anomaly"
    EVIDENCE_EXPIRY = "evidence_expiry"
    DEPENDENCY_CHANGE = "dependency_change"
    PRIVACY_INCIDENT = "privacy_incident"
    CUSTOM = "custom"


class MonitorStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


# ── Models ───────────────────────────────────────────────────────────


class TrustMonitor(Base):
    __tablename__ = "trust_monitors"
    __table_args__ = (
        Index("ix_trust_monitor_org", "org_id"),
        Index("ix_trust_monitor_system", "system_id"),
        Index("ix_trust_monitor_type", "org_id", "monitor_type"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    monitor_type: Mapped[MonitorType] = mapped_column(
        Enum(MonitorType, name="trust_monitor_type", create_constraint=True), nullable=False
    )
    status: Mapped[MonitorStatus] = mapped_column(
        Enum(MonitorStatus, name="trust_monitor_status", create_constraint=True),
        nullable=False,
        default=MonitorStatus.ACTIVE,
    )
    # Threshold configuration
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    alert_severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="trust_alert_severity", create_constraint=True),
        nullable=False,
        default=AlertSeverity.WARNING,
    )
    check_interval_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=60
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


class MonitorAlert(Base):
    """Triggered alerts — append-only log of monitor firings."""

    __tablename__ = "trust_monitor_alerts"
    __table_args__ = (
        Index("ix_trust_alert_org_created", "org_id", "created_at"),
        Index("ix_trust_alert_monitor", "monitor_id"),
        Index("ix_trust_alert_severity_status", "severity", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    monitor_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_monitors.id", ondelete="SET NULL"), nullable=False
    )
    system_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="trust_alert_severity", create_constraint=False), nullable=False
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="trust_alert_status", create_constraint=True),
        nullable=False,
        default=AlertStatus.OPEN,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    metric_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    threshold: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    incident_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    acknowledged_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

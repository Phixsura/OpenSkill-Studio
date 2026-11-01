"""Incident & Remediation Lifecycle models (ADR-017 Part J).

Incident lifecycle records linked to monitoring alerts, with
containment, investigation, remediation, and closure stages.
Emergency controls: pause capability, revoke app, rollback release.
"""

import enum
from datetime import datetime

from sqlalchemy import (
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


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    REPORTED = "reported"
    TRIAGING = "triaging"
    CONTAINED = "contained"
    INVESTIGATING = "investigating"
    REMEDIATING = "remediating"
    VALIDATING = "validating"
    CLOSED = "closed"


class ActionType(str, enum.Enum):
    PAUSE_CAPABILITY = "pause_capability"
    REVOKE_APP = "revoke_app"
    DISABLE_PROVIDER = "disable_provider"
    ROLLBACK_RELEASE = "rollback_release"
    RESTRICT_PERMISSIONS = "restrict_permissions"
    CONTAINMENT = "containment"
    INVESTIGATION = "investigation"
    REMEDIATION = "remediation"
    VALIDATION = "validation"
    COMMUNICATION = "communication"
    POST_INCIDENT = "post_incident"


class ActionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ── Models ───────────────────────────────────────────────────────────


class TrustIncident(Base):
    __tablename__ = "trust_incidents"
    __table_args__ = (
        Index("ix_trust_incident_org_status", "org_id", "status"),
        Index("ix_trust_incident_severity", "severity"),
        Index("ix_trust_incident_system", "system_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="trust_incident_severity", create_constraint=True),
        nullable=False,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="trust_incident_status", create_constraint=True),
        nullable=False,
        default=IncidentStatus.REPORTED,
    )
    # Impact tracking
    impact: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    affected_tenants: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    affected_versions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # Root cause & resolution
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    # People
    reported_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Timeline
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    contained_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class IncidentAction(Base):
    """Remediation actions — append-only log of actions taken."""

    __tablename__ = "trust_incident_actions"
    __table_args__ = (
        Index("ix_trust_inc_action_incident", "incident_id"),
        Index("ix_trust_inc_action_type", "action_type"),
    )

    id: Mapped[str] = ulid_pk()
    incident_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_incidents.id", ondelete="CASCADE"), nullable=False
    )
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="trust_incident_action_type", create_constraint=True),
        nullable=False,
    )
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, name="trust_incident_action_status", create_constraint=True),
        nullable=False,
        default=ActionStatus.PENDING,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # What was affected
    target_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # Execution
    performed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

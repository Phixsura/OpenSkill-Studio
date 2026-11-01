"""Threat Modeling & Red-Team Workbench models (ADR-017 Part E).

Reusable threat models and adversarial test suites run in isolated
environments. Stores fixtures, severity, exploitability, affected
versions, mitigations and regression-test links.
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


class ThreatCategory(str, enum.Enum):
    PROMPT_INJECTION = "prompt_injection"
    INDIRECT_INSTRUCTION = "indirect_instruction"
    DATA_EXFILTRATION = "data_exfiltration"
    CROSS_TENANT_LEAKAGE = "cross_tenant_leakage"
    UNSAFE_TOOL_INVOCATION = "unsafe_tool_invocation"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    COMPROMISED_COMPONENT = "compromised_component"
    DEPENDENCY_TAMPERING = "dependency_tampering"
    UNTRUSTED_OUTPUT = "untrusted_output"
    MODEL_DRIFT = "model_drift"
    AUTOMATION_ABUSE = "automation_abuse"
    CUSTOM = "custom"


class ThreatSeverity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"
    FIXED = "fixed"


# ── Models ───────────────────────────────────────────────────────────


class ThreatModel(Base):
    """Reusable threat model for a category of AI risk."""

    __tablename__ = "trust_threat_models"
    __table_args__ = (
        Index("ix_trust_threat_org", "org_id"),
        Index("ix_trust_threat_category", "category"),
        Index("ix_trust_threat_system", "system_id"),
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
    category: Mapped[ThreatCategory] = mapped_column(
        Enum(ThreatCategory, name="trust_threat_category", create_constraint=True), nullable=False
    )
    # Threat details
    attack_vectors: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    preconditions: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    mitigations: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    affected_components: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    severity: Mapped[ThreatSeverity] = mapped_column(
        Enum(ThreatSeverity, name="trust_threat_severity", create_constraint=True),
        nullable=False,
        default=ThreatSeverity.MEDIUM,
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


class RedTeamSuite(Base):
    """Adversarial test suite with reproducible fixtures."""

    __tablename__ = "trust_redteam_suites"
    __table_args__ = (
        Index("ix_trust_redteam_org", "org_id"),
        Index("ix_trust_redteam_threat", "threat_model_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    threat_model_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("trust_threat_models.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Test fixtures — reproducible adversarial inputs
    fixtures: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    # Isolation constraints
    isolation_config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )  # cpu_limit, memory_limit, timeout, network_policy
    test_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RedTeamRun(Base):
    """Execution record of a red-team test suite."""

    __tablename__ = "trust_redteam_runs"
    __table_args__ = (
        Index("ix_trust_rtrun_org", "org_id", "created_at"),
        Index("ix_trust_rtrun_suite", "suite_id"),
        Index("ix_trust_rtrun_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(String(26), nullable=False)
    suite_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_redteam_suites.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    status: Mapped[TestRunStatus] = mapped_column(
        Enum(TestRunStatus, name="trust_testrun_status", create_constraint=True),
        nullable=False,
        default=TestRunStatus.PENDING,
    )
    # Results
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    total_tests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Execution
    started_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RedTeamFinding(Base):
    """Individual finding from a red-team run."""

    __tablename__ = "trust_redteam_findings"
    __table_args__ = (
        Index("ix_trust_rtfinding_run", "run_id"),
        Index("ix_trust_rtfinding_severity", "severity"),
        Index("ix_trust_rtfinding_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    run_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_redteam_runs.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[ThreatSeverity] = mapped_column(
        Enum(ThreatSeverity, name="trust_threat_severity", create_constraint=False), nullable=False
    )
    status: Mapped[FindingStatus] = mapped_column(
        Enum(FindingStatus, name="trust_finding_status", create_constraint=True),
        nullable=False,
        default=FindingStatus.OPEN,
    )
    # Details
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    exploit_detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    affected_versions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    mitigation: Mapped[str | None] = mapped_column(Text, nullable=True)
    regression_test_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

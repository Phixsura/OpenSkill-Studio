"""Governance Templates, Compliance Reporting & Tenant Policies (ADR-017 Parts L, M, N).

Reusable governance profiles by tenant/region/deployment type, generated
compliance report snapshots, and per-tenant policy overrides with
inheritance, versioning, and conflict explanations.
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


class TemplateScope(str, enum.Enum):
    GLOBAL = "global"
    REGION = "region"
    TENANT = "tenant"
    CAPABILITY_CLASS = "capability_class"
    DEPLOYMENT_TYPE = "deployment_type"


class TemplateStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class ReportType(str, enum.Enum):
    SYSTEM_INVENTORY = "system_inventory"
    RISK_ASSESSMENTS = "risk_assessments"
    APPROVAL_HISTORY = "approval_history"
    ASSURANCE_CASES = "assurance_cases"
    EVIDENCE_GAPS = "evidence_gaps"
    EVALUATION_RESULTS = "evaluation_results"
    DATA_FLOW_SUMMARY = "data_flow_summary"
    HUMAN_OVERSIGHT = "human_oversight"
    INCIDENT_SUMMARY = "incident_summary"
    EXCEPTION_LOG = "exception_log"
    FULL_COMPLIANCE = "full_compliance"


class ReportStatus(str, enum.Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class PolicyOverrideType(str, enum.Enum):
    RISK_THRESHOLD = "risk_threshold"
    GATE_REQUIREMENT = "gate_requirement"
    GUARDRAIL_CONFIG = "guardrail_config"
    REVIEW_REQUIREMENT = "review_requirement"
    MONITORING_CONFIG = "monitoring_config"
    DATA_RESIDENCY = "data_residency"
    RETENTION_POLICY = "retention_policy"


# ── Models ───────────────────────────────────────────────────────────


class GovernanceTemplate(Base):
    """Reusable governance profile for tenant/region/deployment/capability."""

    __tablename__ = "trust_governance_templates"
    __table_args__ = (
        Index("ix_trust_template_org", "org_id"),
        Index("ix_trust_template_scope", "scope"),
        Index("ix_trust_template_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )  # NULL = platform template
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope: Mapped[TemplateScope] = mapped_column(
        Enum(TemplateScope, name="trust_template_scope", create_constraint=True), nullable=False
    )
    scope_value: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # e.g. "EU", "production", "code_execution"
    status: Mapped[TemplateStatus] = mapped_column(
        Enum(TemplateStatus, name="trust_template_status", create_constraint=True),
        nullable=False,
        default=TemplateStatus.DRAFT,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    # Template content — policies, gates, guardrails, review requirements
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Inheritance
    parent_template_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("trust_governance_templates.id", ondelete="SET NULL"), nullable=True
    )
    is_restrictive: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )  # True = cannot be relaxed by child templates
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ComplianceReport(Base):
    """Generated compliance report snapshot — immutable once completed."""

    __tablename__ = "trust_compliance_reports"
    __table_args__ = (
        Index("ix_trust_report_org", "org_id"),
        Index("ix_trust_report_type", "org_id", "report_type"),
        Index("ix_trust_report_created", "org_id", "created_at"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType, name="trust_report_type", create_constraint=True), nullable=False
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="trust_report_status", create_constraint=True),
        nullable=False,
        default=ReportStatus.GENERATING,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Report content — snapshot of data at generation time
    content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Filters/scope used for generation
    filters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Metadata
    system_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    finding_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TenantPolicyOverride(Base):
    """Per-tenant policy override — more restrictive constraints cannot be bypassed."""

    __tablename__ = "trust_tenant_policies"
    __table_args__ = (
        Index("ix_trust_tenant_policy_org", "org_id"),
        Index("ix_trust_tenant_policy_type", "org_id", "override_type"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    override_type: Mapped[PolicyOverrideType] = mapped_column(
        Enum(PolicyOverrideType, name="trust_policy_override_type", create_constraint=True),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Override configuration
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Source template (if derived)
    template_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("trust_governance_templates.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

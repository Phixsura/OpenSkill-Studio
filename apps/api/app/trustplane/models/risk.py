"""Risk Classification models (ADR-017 Part B).

Configurable, versioned risk assessments with separation-of-duty enforcement.
Assessments are append-only — new assessment = new row (never mutate scores).
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
from app.trustplane.models.inventory import RiskTier


class AssessmentStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class RiskScoringPolicy(Base):
    __tablename__ = "trust_risk_scoring_policies"
    __table_args__ = (
        Index(
            "uq_trust_policy_org_active",
            "org_id",
            unique=True,
            postgresql_where="is_active = true",
        ),
        Index("ix_trust_policy_org", "org_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    dimensions: Mapped[list] = mapped_column(JSONB, nullable=False)
    tier_thresholds: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RiskAssessment(Base):
    __tablename__ = "trust_risk_assessments"
    __table_args__ = (
        CheckConstraint(
            "assessed_by != reviewed_by OR reviewed_by IS NULL",
            name="ck_trust_assessment_separation_of_duty",
        ),
        CheckConstraint("version >= 1", name="ck_trust_assessment_version_positive"),
        Index("ix_trust_assessment_system_status", "system_id", "status"),
        Index("uq_trust_assessment_system_version", "system_id", "version", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    system_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False
    )
    policy_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("trust_risk_scoring_policies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus, name="trust_assessment_status", create_constraint=True),
        nullable=False,
        default=AssessmentStatus.DRAFT,
    )
    dimension_scores: Mapped[dict] = mapped_column(JSONB, nullable=False)
    weighted_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    computed_tier: Mapped[RiskTier | None] = mapped_column(
        Enum(RiskTier, name="trust_risk_tier", create_constraint=False), nullable=True
    )
    override_tier: Mapped[RiskTier | None] = mapped_column(
        Enum(RiskTier, name="trust_risk_tier", create_constraint=False), nullable=True
    )
    effective_tier: Mapped[RiskTier | None] = mapped_column(
        Enum(RiskTier, name="trust_risk_tier", create_constraint=False), nullable=True
    )
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessed_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ── Default scoring dimensions ───────────────────────────────────────

DEFAULT_DIMENSIONS = [
    {
        "key": "autonomy",
        "label": "Level of Autonomy",
        "description": "How independently does the system act?",
        "weight": 1.0,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=advisory only, 2=suggestions with confirmation, 3=auto with human override, 4=autonomous with monitoring, 5=fully autonomous",
    },
    {
        "key": "data_sensitivity",
        "label": "Data Sensitivity",
        "description": "Sensitivity of data the system processes or generates.",
        "weight": 1.5,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=public data only, 2=internal data, 3=confidential, 4=sensitive PII, 5=highly sensitive (health, financial, biometric)",
    },
    {
        "key": "impact_reversibility",
        "label": "Impact & Reversibility",
        "description": "Severity and reversibility of the system's effects.",
        "weight": 1.5,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=trivially reversible, 2=easily corrected, 3=correctable with effort, 4=partially irreversible, 5=fully irreversible (legal, financial, safety)",
    },
    {
        "key": "tool_access",
        "label": "Tool & System Access",
        "description": "Scope of tools, APIs, and systems the AI can invoke.",
        "weight": 1.0,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=no tool access, 2=read-only APIs, 3=sandboxed writes, 4=production writes, 5=admin/infrastructure access",
    },
    {
        "key": "blast_radius",
        "label": "Scale & Blast Radius",
        "description": "Number of users, tenants, or systems affected.",
        "weight": 1.2,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=single user, 2=small team, 3=single org, 4=multiple orgs, 5=platform-wide or public-facing",
    },
    {
        "key": "uncertainty",
        "label": "Uncertainty & Confidence",
        "description": "How uncertain or unpredictable the system's behavior is.",
        "weight": 1.0,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=deterministic, 2=low variance, 3=moderate variance, 4=high variance, 5=novel/untested domain",
    },
    {
        "key": "eval_coverage",
        "label": "Evaluation Coverage",
        "description": "Extent of testing and evaluation evidence available.",
        "weight": 0.8,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=comprehensive benchmarks, 2=good test coverage, 3=partial coverage, 4=minimal testing, 5=no evaluation evidence",
    },
    {
        "key": "supply_chain",
        "label": "Supply-Chain Exposure",
        "description": "Dependency on third-party models, data, or components.",
        "weight": 1.0,
        "scale_min": 1,
        "scale_max": 5,
        "guidance": "1=fully internal, 2=vetted vendors, 3=mixed sources, 4=third-party models, 5=unvetted external components",
    },
]

DEFAULT_TIER_THRESHOLDS = {
    "minimal": {"max_score": 1.5},
    "low": {"max_score": 2.5},
    "medium": {"max_score": 3.5},
    "high": {"max_score": 4.5},
    "critical": {"min_score": 4.5},
}

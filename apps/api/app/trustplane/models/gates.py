"""Evaluation & Release Gates models (ADR-017 Part D).

Reusable assurance profiles define what checks must pass before a
component can be published, approved, installed, promoted or deployed.
Gate results record each evaluation with pass/fail/skip outcomes.
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


class GateTrigger(str, enum.Enum):
    PUBLISH_PACK = "publish_pack"
    APPROVE_APP = "approve_app"
    INSTALL_TENANT = "install_tenant"
    ENABLE_PROVIDER = "enable_provider"
    PROMOTE_EXPERIMENT = "promote_experiment"
    INCREASE_AUTONOMY = "increase_autonomy"
    ACCEPT_FEDERATED = "accept_federated"
    DEPLOY_SYSTEM = "deploy_system"


class CheckType(str, enum.Enum):
    DETERMINISTIC = "deterministic"     # automated pass/fail
    EVALUATION = "evaluation"           # AI/benchmark evidence required
    POLICY = "policy"                   # policy-as-code check
    HUMAN_REVIEW = "human_review"       # manual review required
    EVIDENCE_REQUIRED = "evidence_required"  # specific evidence must exist


class GateOutcome(str, enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"         # check not applicable
    OVERRIDDEN = "overridden"   # failed but overridden with justification


class ProfileStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


# ── Models ───────────────────────────────────────────────────────────


class AssuranceProfile(Base):
    """Reusable template defining what checks must pass for a gate trigger."""

    __tablename__ = "trust_assurance_profiles"
    __table_args__ = (
        Index("ix_trust_profile_org", "org_id"),
        Index("ix_trust_profile_trigger", "org_id", "trigger"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )  # NULL = platform default
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger: Mapped[GateTrigger] = mapped_column(
        Enum(GateTrigger, name="trust_gate_trigger", create_constraint=True), nullable=False
    )
    status: Mapped[ProfileStatus] = mapped_column(
        Enum(ProfileStatus, name="trust_profile_status", create_constraint=True),
        nullable=False,
        default=ProfileStatus.DRAFT,
    )
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


class GateCheck(Base):
    """A single check within an assurance profile."""

    __tablename__ = "trust_gate_checks"
    __table_args__ = (
        Index("ix_trust_check_profile", "profile_id"),
    )

    id: Mapped[str] = ulid_pk()
    profile_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_assurance_profiles.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    check_type: Mapped[CheckType] = mapped_column(
        Enum(CheckType, name="trust_check_type", create_constraint=True), nullable=False
    )
    is_blocking: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )  # if True, failure blocks the gate
    config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class GateResult(Base):
    """Result of evaluating a gate for a specific target entity."""

    __tablename__ = "trust_gate_results"
    __table_args__ = (
        Index("ix_trust_gate_result_target", "target_type", "target_id"),
        Index("ix_trust_gate_result_profile", "profile_id"),
        Index("ix_trust_gate_result_org", "org_id", "created_at"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    profile_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_assurance_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    # What was evaluated
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[str] = mapped_column(String(26), nullable=False)
    target_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Overall outcome
    outcome: Mapped[GateOutcome] = mapped_column(
        Enum(GateOutcome, name="trust_gate_outcome", create_constraint=True),
        nullable=False,
        default=GateOutcome.PENDING,
    )
    # Per-check results
    check_results: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    # Override
    override_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    evaluated_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

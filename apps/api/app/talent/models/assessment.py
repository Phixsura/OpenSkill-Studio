"""Assessments and credentials — standardized evaluation + verifiable issuance (ADR-015 D5).

Assessment blueprints are reusable definitions. Runs are user attempts.
Credentials are issued when versioned rules are satisfied.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class AssessmentBlueprint(Base):
    """Reusable standardized assessment definition."""

    __tablename__ = "assessment_blueprints"


    def __repr__(self) -> str:
        return f"<AssessmentBlueprint {self.id}>"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # knowledge | practical_task | portfolio_review | workflow_execution |
    # commercial_simulation | multi_stage_challenge
    assessment_type: Mapped[str] = mapped_column(String(30))
    # [{"capability_id": "01J...", "min_level": 3, "weight": 0.4}]
    capability_requirements: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # time_window_minutes, attempt_limit, required_deliverables,
    # rubric_id, workflow_restrictions, provider_restrictions,
    # human_review_required, reference_assets, auto_issue_credential
    config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    # draft | active | archived
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="'draft'")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_assessment_blueprints_org", "org_id", "status"),)


class AssessmentRun(Base):
    """A user's attempt at a specific assessment blueprint version."""

    __tablename__ = "assessment_runs"


    def __repr__(self) -> str:
        return f"<AssessmentRun {self.id}>"

    id: Mapped[str] = ulid_pk()
    blueprint_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("assessment_blueprints.id", ondelete="CASCADE")
    )
    blueprint_version: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    # not_started | in_progress | submitted | under_review | passed | failed | expired
    status: Mapped[str] = mapped_column(
        String(20), default="not_started", server_default="'not_started'"
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # [{"capability_id": "01J...", "score": 0.85, "passed": true}]
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Loose ref to project/submission created for practical assessments
    project_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_assessment_runs_user", "user_id", "blueprint_id"),
        Index("ix_assessment_runs_org", "org_id", "status"),
    )


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------


class CredentialRule(Base):
    """Versioned rule set for credential issuance — immutable once active."""

    __tablename__ = "credential_rules"


    def __repr__(self) -> str:
        return f"<CredentialRule {self.id}>"

    id: Mapped[str] = ulid_pk()
    credential_type: Mapped[str] = mapped_column(String(80))
    version: Mapped[int] = mapped_column(Integer)
    # Display metadata
    display_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # [{"capability_id": "01J...", "min_level": 3},
    #  {"assessment_blueprint_id": "01J...", "required": true}]
    requirements: Mapped[list] = mapped_column(JSONB, server_default="[]")
    # min_evidence_count, min_verification_level,
    # required_assessment_types, all_required (AND) vs any_required (OR),
    # auto_issue, validity_days
    conditions: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Org that owns this rule (NULL = platform-level)
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    # draft | active | retired
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="'draft'")
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("uq_credential_rule_version", "credential_type", "version", unique=True),
    )


class Credential(Base):
    """Verified credential issued when a versioned rule set is satisfied."""

    __tablename__ = "credentials"


    def __repr__(self) -> str:
        return f"<Credential {self.id}>"

    id: Mapped[str] = ulid_pk()
    credential_type: Mapped[str] = mapped_column(String(80))
    version: Mapped[int] = mapped_column(Integer, default=1)
    # Rule that was satisfied (for audit)
    credential_rule_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("credential_rules.id", ondelete="SET NULL"), nullable=True
    )
    issuer_org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    # [{"capability_id": "01J...", "required_level": 3, "achieved_level": 4}]
    capabilities: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Assessment/evidence IDs that satisfied the rule
    evidence_references: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # active | expired | revoked | superseded
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revalidation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_credentials_user", "user_id", "status"),
        Index("ix_credentials_type", "credential_type", "version"),
        # One active credential per (user, type)
        Index(
            "uq_credential_active",
            "user_id",
            "credential_type",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

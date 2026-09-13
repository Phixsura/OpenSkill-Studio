"""Verified evidence ledger — append-only proof of capability (ADR-015 D2).

Evidence rows are immutable. Corrections occur via superseding/void events,
not silent mutation. The only allowed UPDATE is status transitions:
active → superseded | voided.
"""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Evidence source types — what generated the evidence
EVIDENCE_SOURCE_TYPES = frozenset(
    {
        "skill_completion",
        "exercise_result",
        "assessment_result",
        "project_approval",
        "rubric_score",
        "peer_review",
        "instructor_verification",
        "multimodal_ai_evaluation",
        "commercial_project_approval",
        "client_acceptance",
        "workflow_execution",
        "credential",
        "employment_verification",
    }
)

# Verification levels — ordered by trust (highest first)
VERIFICATION_LEVELS = (
    "employer_verified",
    "client_verified",
    "assessment_verified",
    "instructor_verified",
    "peer_verified",
    "system_observed",
    "self_reported",
)

# Weights used in scoring — higher-trust evidence contributes more
VERIFICATION_WEIGHTS: dict[str, float] = {
    "employer_verified": 1.00,
    "client_verified": 0.95,
    "assessment_verified": 0.90,
    "instructor_verified": 0.85,
    "peer_verified": 0.70,
    "system_observed": 0.60,
    "self_reported": 0.30,
}


class CapabilityEvidence(Base):
    """Append-only proof that a user demonstrated a capability."""

    __tablename__ = "capability_evidence"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    capability_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    source_type: Mapped[str] = mapped_column(String(40))
    source_id: Mapped[str] = mapped_column(String(26))
    # Org where the evidence was earned (informational, not ownership)
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    # Normalized to [0, 1]. NULL when binary (pass/fail).
    score_normalized: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    # System confidence in this evidence item [0, 1]
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), default=1.0, server_default="1.0000")
    verification_level: Mapped[str] = mapped_column(String(30))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Immutability: corrections via supersede/void
    supersedes_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # active | superseded | voided
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    # Provenance, additional scores, rubric details, etc.
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())

    __table_args__ = (
        Index("ix_cap_evidence_user_cap", "user_id", "capability_id", "status"),
        Index("ix_cap_evidence_source", "source_type", "source_id"),
        Index("ix_cap_evidence_org", "org_id", "capability_id"),
        Index("ix_cap_evidence_occurred", "user_id", "occurred_at"),
        # Idempotency: one active evidence per (user, capability, source_type, source_id)
        Index(
            "uq_cap_evidence_idempotent",
            "user_id",
            "capability_id",
            "source_type",
            "source_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        CheckConstraint(
            "score_normalized IS NULL OR (score_normalized >= 0 AND score_normalized <= 1)",
            name="ck_evidence_score_range",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_evidence_confidence_range",
        ),
    )

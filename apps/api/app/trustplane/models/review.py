"""Human Oversight & Approval models (ADR-017 Part H).

Review requests with separation of duty, documented rationale,
expiring exceptions, and append-only decision records.
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


class ReviewType(str, enum.Enum):
    RISK_ASSESSMENT = "risk_assessment"
    RELEASE_GATE = "release_gate"
    EVIDENCE_REVIEW = "evidence_review"
    EXCEPTION_REQUEST = "exception_request"
    INCIDENT_CLOSURE = "incident_closure"
    POLICY_CHANGE = "policy_change"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETURNED = "returned"    # sent back for more info
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ReviewDecisionType(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    RETURN = "return"
    ESCALATE = "escalate"


# ── Models ───────────────────────────────────────────────────────────


class ReviewRequest(Base):
    """A request for human review/approval of a trust-related decision."""

    __tablename__ = "trust_review_requests"
    __table_args__ = (
        Index("ix_trust_review_org_status", "org_id", "status"),
        Index("ix_trust_review_target", "target_type", "target_id"),
        Index("ix_trust_review_assignee", "assigned_to"),
        Index("ix_trust_review_due", "due_at"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    review_type: Mapped[ReviewType] = mapped_column(
        Enum(ReviewType, name="trust_review_type", create_constraint=True), nullable=False
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="trust_review_status", create_constraint=True),
        nullable=False,
        default=ReviewStatus.PENDING,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # What is being reviewed
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[str] = mapped_column(String(26), nullable=False)
    # Who
    requested_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Context
    context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ReviewDecision(Base):
    """Append-only record of a review decision — immutable once written."""

    __tablename__ = "trust_review_decisions"
    __table_args__ = (
        Index("ix_trust_decision_request", "request_id"),
        Index("ix_trust_decision_reviewer", "reviewer_id"),
    )

    id: Mapped[str] = ulid_pk()
    request_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_review_requests.id", ondelete="CASCADE"), nullable=False
    )
    decision: Mapped[ReviewDecisionType] = mapped_column(
        Enum(ReviewDecisionType, name="trust_review_decision_type", create_constraint=True),
        nullable=False,
    )
    reviewer_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

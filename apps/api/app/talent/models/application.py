"""Application / placement pipeline — full lifecycle with audit (ADR-015 D8).

Every status transition requires an authenticated user (acted_by). No
automatic hire/reject/offer transitions exist.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Application state machine — every transition is authorized + audited
APPLICATION_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["submitted", "withdrawn"],
    "submitted": ["screening", "rejected", "withdrawn"],
    "screening": ["interview", "assessment", "rejected", "withdrawn"],
    "interview": ["assessment", "offer", "rejected", "withdrawn"],
    "assessment": ["interview", "offer", "rejected", "withdrawn"],
    "offer": ["accepted", "rejected", "withdrawn"],
    "accepted": ["hired", "withdrawn"],
    "rejected": [],
    "withdrawn": [],
    "hired": ["completed"],
    "completed": [],
}

TERMINAL_STATUSES = frozenset({"rejected", "withdrawn", "completed"})


class Application(Base):
    """Candidate's application to an opportunity."""

    __tablename__ = "applications"

    id: Mapped[str] = ulid_pk()
    opportunity_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    # Frozen at submission — future passport changes don't update this
    evidence_bundle: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    passport_snapshot_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("passport_snapshots.id", ondelete="SET NULL"), nullable=True
    )
    # Provenance: which match run surfaced this
    match_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="'draft'")
    resume_asset_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    cover_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        # One application per (user, opportunity)
        Index("uq_application", "user_id", "opportunity_id", unique=True),
        Index("ix_applications_opportunity", "opportunity_id", "status"),
        Index("ix_applications_user", "user_id", "status"),
    )


class ApplicationEvent(Base):
    """Audit trail for application status changes."""

    __tablename__ = "application_events"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE")
    )
    from_status: Mapped[str] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20))
    # NOT nullable — every transition requires an authenticated actor
    acted_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (Index("ix_app_events_application", "application_id", "created_at"),)


class InterviewStage(Base):
    """Structured interview/evaluation record — employer-private notes."""

    __tablename__ = "interview_stages"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE")
    )
    # phone | technical | portfolio | panel | final
    stage_type: Mapped[str] = mapped_column(String(30))
    interviewer_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meeting_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Employer-private — NEVER exposed to other employers or candidates
    evaluation_notes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # pending | completed | cancelled | no_show
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="'pending'")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (Index("ix_interview_stages_app", "application_id"),)


class Placement(Base):
    """Outcome record when an application reaches hired status."""

    __tablename__ = "placements"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE"), unique=True
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    employer_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    role_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Privacy-controlled: only visible to user and employer admin
    compensation_band: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # platform_match | direct_apply | referral | cohort_exposure
    placement_source: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # active | completed | terminated | cancelled
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_placements_user", "user_id"),
        Index("ix_placements_employer", "employer_org_id", "status"),
    )


# ---------------------------------------------------------------------------
# Application feedback (N8)
# ---------------------------------------------------------------------------

FEEDBACK_TYPES = frozenset({"rejection_reason", "interview_feedback", "general"})
FEEDBACK_VISIBILITY = frozenset({"employer_only", "shared_with_candidate"})


class ApplicationFeedback(Base):
    """Structured feedback on an application — visibility controlled.

    employer_only: visible only to the employer org members.
    shared_with_candidate: visible to the applicant as well.
    """

    __tablename__ = "talent_application_feedback"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE")
    )
    feedback_type: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(
        String(30), default="employer_only", server_default="'employer_only'"
    )
    author_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_app_feedback_app", "application_id"),
        Index("ix_app_feedback_author", "author_id"),
    )

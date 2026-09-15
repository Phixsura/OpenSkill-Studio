"""Internship supervision, employer verification, outcome events (ADR-015 D9–D10).

Covers cohort-to-opportunity exposure, school-side tracking, employer
verification → evidence generation, and longitudinal outcome events.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class CohortOpportunityExposure(Base):
    """School recommends/exposes an opportunity to a cohort.

    Exposure does NOT share student data — students must individually
    opt in (discoverable=true + apply) before employer sees anything.
    """

    __tablename__ = "cohort_opportunity_exposures"

    id: Mapped[str] = ulid_pk()
    cohort_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="CASCADE")
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="CASCADE")
    )
    exposed_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())

    __table_args__ = (
        Index("uq_cohort_exposure", "cohort_id", "opportunity_id", unique=True),
    )


class InternshipSupervision(Base):
    """School-side tracking of an internship placement."""

    __tablename__ = "internship_supervisions"

    id: Mapped[str] = ulid_pk()
    placement_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("placements.id", ondelete="CASCADE"), unique=True
    )
    school_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    supervisor_user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    employer_mentor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # [{"title": "...", "due_date": "...", "status": "pending|done"}]
    milestones: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # [{"date": "...", "type": "weekly_checkin|note", "text": "..."}]
    notes: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # pending | active | completed | terminated
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="'pending'")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_supervisions_school", "school_org_id", "status"),)


class EmployerVerification(Base):
    """Structured capability verification from an employer after a placement.

    On creation, auto-generates capability_evidence rows with
    source_type='employment_verification', verification_level='employer_verified'.
    """

    __tablename__ = "employer_verifications"

    id: Mapped[str] = ulid_pk()
    placement_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("placements.id", ondelete="CASCADE")
    )
    employer_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    verified_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # [{"capability_id": "01J...", "level_observed": 4, "score": 0.85, "comment": "..."}]
    capability_ratings: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    overall_rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    overall_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())

    __table_args__ = (
        Index("ix_employer_verifications_placement", "placement_id"),
        Index("ix_employer_verifications_user", "user_id"),
    )


# ---------------------------------------------------------------------------
# Outcome events (longitudinal career milestones)
# ---------------------------------------------------------------------------

OUTCOME_EVENT_TYPES = frozenset(
    {
        "internship_started",
        "internship_completed",
        "job_offer_received",
        "job_started",
        "contract_project_completed",
        "promotion",
        "role_change",
        "credential_renewed",
        "capability_reverified",
    }
)


class OutcomeEvent(Base):
    """Longitudinal career milestone — user-controlled visibility."""

    __tablename__ = "outcome_events"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(String(40))
    source_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # private | passport_visible | public
    visibility: Mapped[str] = mapped_column(String(20), default="private", server_default="'private'")
    extra: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, server_default="{}")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())

    __table_args__ = (Index("ix_outcome_events_user", "user_id", "event_type"),)

"""Structured interview scorecards — rubric-based evaluation (Phase 4D).

Templates define evaluation criteria (name, weight, rubric) for an org.
Scorecards capture an interviewer's per-criterion ratings for a specific
interview stage, with an overall recommendation.
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

RECOMMENDATIONS = frozenset({"strong_hire", "hire", "no_hire", "strong_no_hire"})


class ScorecardTemplate(Base):
    """Org-level interview rubric template.

    criteria JSON example::

        [
            {"name": "Technical Skills", "weight": 0.4, "rubric": "1-5 scale ..."},
            {"name": "Communication", "weight": 0.3, "rubric": "1-5 scale ..."},
            {"name": "Culture Fit", "weight": 0.3, "rubric": "1-5 scale ..."},
        ]
    """

    __tablename__ = "talent_scorecard_templates"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria: Mapped[list] = mapped_column(JSONB, default=list, server_default="'[]'")
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_scorecard_tmpl_org", "org_id"),)


class InterviewScorecard(Base):
    """Per-interview-stage evaluation scorecard.

    ratings JSON example::

        {
            "Technical Skills": {"score": 4, "notes": "Strong algo skills"},
            "Communication": {"score": 3, "notes": "Clear but could elaborate"},
        }
    """

    __tablename__ = "talent_interview_scorecards"

    id: Mapped[str] = ulid_pk()
    interview_stage_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("interview_stages.id", ondelete="CASCADE")
    )
    template_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey("talent_scorecard_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    interviewer_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    ratings: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="'{}'")
    overall_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_scorecard_interview", "interview_stage_id"),
        Index("ix_scorecard_interviewer", "interviewer_id"),
    )

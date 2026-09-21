"""Interview scheduling — time slot proposals, acceptance, and calendar integration.

Supports multi-slot proposals (employer proposes N times, candidate picks one),
automatic decline of un-picked slots, and .ics calendar invite generation.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

SLOT_STATUSES = frozenset({"proposed", "accepted", "declined", "cancelled"})


class InterviewSlot(Base):
    """A proposed time slot for an interview stage."""

    __tablename__ = "talent_interview_slots"

    def __repr__(self) -> str:
        return f"<InterviewSlot {self.id}>"

    id: Mapped[str] = ulid_pk()
    interview_stage_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("interview_stages.id", ondelete="CASCADE")
    )
    proposed_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="proposed", server_default="'proposed'")
    meeting_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meeting_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    accepted_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_interview_slots_stage", "interview_stage_id", "status"),
        Index("ix_interview_slots_proposed_by", "proposed_by"),
    )

"""Candidate notes model — employer-side CRM notes on candidates (N4).

Notes are org-scoped and never visible to the candidate.
Only the author can edit/delete their own notes.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class CandidateNote(Base):
    """An employer-side note about a candidate."""

    __tablename__ = "talent_candidate_notes"

    def __repr__(self) -> str:
        return f"<CandidateNote {self.id}>"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    candidate_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    author_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    opportunity_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True
    )
    note_text: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_candidate_notes_org_user", "org_id", "candidate_user_id"),
        Index("ix_candidate_notes_author", "author_id"),
    )

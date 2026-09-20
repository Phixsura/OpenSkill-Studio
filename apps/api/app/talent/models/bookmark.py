"""Opportunity bookmark model — saved opportunities for candidates (N13)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class OpportunityBookmark(Base):
    __tablename__ = "talent_opportunity_bookmarks"

    def __repr__(self) -> str:
        return f"<OpportunityBookmark {self.id}>"

    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="uq_user_opportunity_bookmark"),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="CASCADE"), index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

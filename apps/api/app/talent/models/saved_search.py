"""Saved search model — persistent search criteria for talent rediscovery."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

SEARCH_TYPES = frozenset({"candidate", "opportunity"})
NOTIFY_FREQUENCIES = frozenset({"never", "daily", "weekly", "on_new_match"})


class SavedSearch(Base):
    __tablename__ = "talent_saved_searches"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    search_type: Mapped[str] = mapped_column(String(20))  # candidate | opportunity
    search_criteria: Mapped[dict] = mapped_column(JSONB, default=dict)
    notify_frequency: Mapped[str] = mapped_column(String(20), default="never")
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

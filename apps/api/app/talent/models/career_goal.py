"""Career goal model — user-side goal tracking (N3).

Users set career aspirations with target capabilities and dates,
then track progress as their capability profile grows.
"""

from __future__ import annotations

from datetime import date, datetime

import ulid
from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

GOAL_STATUSES = frozenset({"active", "completed", "abandoned"})
MAX_ACTIVE_GOALS = 5


class CareerGoal(Base):
    __tablename__ = "talent_career_goals"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=lambda: ulid.new().str
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_role: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # [{capability_id, capability_name, target_level}]
    target_capabilities: Mapped[list] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

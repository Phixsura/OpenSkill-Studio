"""Onboarding workflow models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class OnboardingTemplate(Base):
    __tablename__ = "talent_onboarding_templates"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(String(26), ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tasks: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OnboardingChecklist(Base):
    __tablename__ = "talent_onboarding_checklists"

    id: Mapped[str] = ulid_pk()
    placement_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("talent_placements.id"), index=True
    )
    template_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("talent_onboarding_templates.id"), nullable=True
    )
    tasks: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    completion_percentage: Mapped[int] = mapped_column(SmallInteger, default=0)
    current_phase: Mapped[str] = mapped_column(String(30), default="pre_start")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

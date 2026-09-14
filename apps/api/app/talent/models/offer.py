"""Offer management models."""

from datetime import datetime

import ulid
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Offer(Base):
    __tablename__ = "talent_offers"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, default=lambda: ulid.new().str)
    application_id: Mapped[str] = mapped_column(String(26), ForeignKey("talent_applications.id"), index=True)
    employer_org_id: Mapped[str] = mapped_column(String(26), ForeignKey("organizations.id"), index=True)
    role_title: Mapped[str] = mapped_column(String(200))
    compensation_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    conditions: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    custom_sections: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    negotiation_history: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    declined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decline_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(26), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

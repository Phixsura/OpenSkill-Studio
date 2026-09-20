"""Succession planning models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class KeyRole(Base):
    __tablename__ = "talent_key_roles"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_capabilities: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    current_holder_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    criticality: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SuccessorNomination(Base):
    __tablename__ = "talent_successor_nominations"

    id: Mapped[str] = ulid_pk()
    key_role_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("talent_key_roles.id", ondelete="CASCADE"), index=True
    )
    candidate_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    readiness: Mapped[str] = mapped_column(String(30), default="not_assessed")
    capability_match: Mapped[float | None] = mapped_column(nullable=True)
    gaps: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    development_plan: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    nominated_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

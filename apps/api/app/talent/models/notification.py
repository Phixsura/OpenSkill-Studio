"""Talent notifications — in-app notification system (ADR-015 upgrade).

Stores per-user notification records and delivery preferences.
Email delivery hooks are supported via the preference model but
actual email sending is delegated to a separate email service.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

NOTIFICATION_EVENT_TYPES = frozenset({
    "application_status_changed",
    "new_match_found",
    "outreach_received",
    "credential_issued",
    "interview_scheduled",
    "offer_extended",
    "endorsement_received",
    "pool_invitation",
    "passport_viewed",
})


class NotificationPreference(Base):
    """Per-user, per-event notification delivery preferences."""

    __tablename__ = "talent_notification_preferences"
    __table_args__ = (
        Index("ix_notif_pref_user", "user_id"),
        Index("ix_notif_pref_user_event", "user_id", "event_type", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    channel: Mapped[str] = mapped_column(String(20), default="in_app")
    event_type: Mapped[str] = mapped_column(String(50))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TalentNotification(Base):
    """In-app notification record for talent lifecycle events."""

    __tablename__ = "talent_notifications"
    __table_args__ = (
        Index("ix_notif_user_created", "user_id", "created_at"),
        Index("ix_notif_user_read", "user_id", "read_at"),
        Index("ix_notif_event_type", "event_type"),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    extra: Mapped[dict] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

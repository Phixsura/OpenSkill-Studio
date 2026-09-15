"""Talent notification service — in-app notifications with email-ready hooks.

Sends in-app notifications for talent lifecycle events. Email delivery
is handled by a separate email service (out of scope here) but the
notification record and preference system supports it.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.notification import (
    NOTIFICATION_EVENT_TYPES,
    NotificationPreference,
    TalentNotification,
)

# Default preferences for new users (all enabled)
_DEFAULT_CHANNEL = "in_app"


class TalentNotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send(
        self,
        *,
        user_id: str,
        event_type: str,
        title: str,
        message: str,
        metadata: dict | None = None,
    ) -> TalentNotification | None:
        """Send an in-app notification, respecting user preferences.

        Returns the notification if sent, None if suppressed by preferences.
        """
        if event_type not in NOTIFICATION_EVENT_TYPES:
            raise ValueError(
                f"Invalid event_type: {event_type}. "
                f"Must be one of {sorted(NOTIFICATION_EVENT_TYPES)}"
            )

        # Check if user has disabled this event type
        pref = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.event_type == event_type,
                NotificationPreference.channel == _DEFAULT_CHANNEL,
            )
        )
        pref_row = pref.scalar_one_or_none()
        if pref_row and not pref_row.enabled:
            return None

        notification = TalentNotification(
            user_id=user_id,
            event_type=event_type,
            title=title,
            message=message,
            extra=metadata or {},
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def list_notifications(
        self,
        user_id: str,
        *,
        unread_only: bool = False,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[TalentNotification], bool]:
        """List notifications for a user, newest first.

        Returns (notifications, has_more).
        """
        q = select(TalentNotification).where(
            TalentNotification.user_id == user_id
        )
        if unread_only:
            q = q.where(TalentNotification.read_at.is_(None))
        if cursor:
            q = q.where(TalentNotification.id < cursor)

        q = q.order_by(TalentNotification.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more

    async def mark_read(
        self, notification_id: str, user_id: str
    ) -> TalentNotification | None:
        """Mark a single notification as read."""
        notif = await self.db.get(TalentNotification, notification_id)
        if not notif or notif.user_id != user_id:
            return None
        if notif.read_at is None:
            notif.read_at = datetime.now(UTC)
            await self.db.flush()
        return notif

    async def mark_all_read(self, user_id: str) -> int:
        """Mark all unread notifications as read. Returns count updated."""
        now = datetime.now(UTC)
        result = await self.db.execute(
            update(TalentNotification)
            .where(
                TalentNotification.user_id == user_id,
                TalentNotification.read_at.is_(None),
            )
            .values(read_at=now)
        )
        await self.db.flush()
        return result.rowcount or 0

    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count for badge display."""
        result = await self.db.execute(
            select(func.count())
            .select_from(TalentNotification)
            .where(
                TalentNotification.user_id == user_id,
                TalentNotification.read_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def get_preferences(
        self, user_id: str
    ) -> list[dict]:
        """Get all notification preferences with defaults for missing types."""
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        existing = {p.event_type: p for p in result.scalars().all()}

        prefs = []
        for event_type in sorted(NOTIFICATION_EVENT_TYPES):
            if event_type in existing:
                p = existing[event_type]
                prefs.append({
                    "event_type": event_type,
                    "channel": p.channel,
                    "enabled": p.enabled,
                })
            else:
                prefs.append({
                    "event_type": event_type,
                    "channel": _DEFAULT_CHANNEL,
                    "enabled": True,
                })
        return prefs

    async def update_preferences(
        self, user_id: str, preferences: list[dict]
    ) -> list[dict]:
        """Bulk update notification preferences.

        Each dict: {"event_type": str, "enabled": bool, "channel": str?}
        """
        for pref in preferences:
            event_type = pref["event_type"]
            if event_type not in NOTIFICATION_EVENT_TYPES:
                raise ValueError(f"Invalid event_type: {event_type}")

            channel = pref.get("channel", _DEFAULT_CHANNEL)
            enabled = pref.get("enabled", True)

            # Upsert
            result = await self.db.execute(
                select(NotificationPreference).where(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.event_type == event_type,
                    NotificationPreference.channel == channel,
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                existing.enabled = enabled
            else:
                self.db.add(
                    NotificationPreference(
                        user_id=user_id,
                        event_type=event_type,
                        channel=channel,
                        enabled=enabled,
                    )
                )

        await self.db.flush()
        return await self.get_preferences(user_id)

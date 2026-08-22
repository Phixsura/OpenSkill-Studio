"""Notification service — create, list, mark-read, preferences."""

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, UserNotificationPreference

log = structlog.get_logger()


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        body: str | None = None,
        org_id: str | None = None,
        data: dict | None = None,
    ) -> Notification | None:
        # Check if user has opted out of this notification type
        prefs = await self.get_preferences(user_id)
        if prefs and prefs.get(notification_type) is False:
            log.debug(
                "notification_suppressed",
                user_id=user_id,
                type=notification_type,
            )
            return None

        notification = Notification(
            user_id=user_id,
            org_id=org_id,
            type=notification_type,
            title=title,
            body=body,
            data=data or {},
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def list_notifications(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 20,
        include_read: bool = False,
    ) -> tuple[list[Notification], int]:
        base = select(Notification).where(Notification.user_id == user_id)
        if not include_read:
            base = base.where(Notification.is_read.is_(False))

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(Notification.created_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    # Keep backward-compatible alias
    async def list_unread(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[Notification], int]:
        return await self.list_notifications(user_id, page, per_page, include_read=False)

    async def mark_read(self, notification_id: str, user_id: str) -> None:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if notification is None:
            from app.exceptions import AppError

            raise AppError("NOTIFICATION_NOT_FOUND", "Notification not found", 404)
        notification.is_read = True
        await self.db.flush()

    async def mark_all_read(self, user_id: str) -> int:
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        await self.db.flush()
        return result.rowcount

    # ── Preferences ──

    _DEFAULT_PREFERENCES: dict = {
        "pack.installed": True,
        "pack.updated": True,
        "pack.approved": True,
        "pack.rejected": True,
        "submission.reviewed": True,
        "cohort.status_changed": True,
        "project.deadline_approaching": True,
    }

    async def get_preferences(self, user_id: str) -> dict:
        result = await self.db.execute(
            select(UserNotificationPreference).where(
                UserNotificationPreference.user_id == user_id
            )
        )
        pref = result.scalar_one_or_none()
        if pref is None:
            return dict(self._DEFAULT_PREFERENCES)
        # Merge: stored prefs override defaults, but defaults fill any gaps
        return {**self._DEFAULT_PREFERENCES, **pref.preferences}

    async def update_preferences(self, user_id: str, preferences: dict) -> dict:
        result = await self.db.execute(
            select(UserNotificationPreference).where(
                UserNotificationPreference.user_id == user_id
            )
        )
        pref = result.scalar_one_or_none()
        if pref is None:
            pref = UserNotificationPreference(
                user_id=user_id,
                preferences=preferences,
            )
            self.db.add(pref)
        else:
            # Merge: update existing keys, keep unmentioned ones
            merged = {**pref.preferences, **preferences}
            pref.preferences = merged
        await self.db.flush()
        return pref.preferences

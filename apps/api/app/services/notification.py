"""Notification service — create, list, mark-read."""

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

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
    ) -> Notification:
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

    async def list_unread(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[Notification], int]:
        base = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(Notification.created_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

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

"""Notification endpoints — list unread, mark read."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.services.notification import NotificationService

router = APIRouter(tags=["Notifications"])


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    org_id: str | None
    type: str
    title: str
    body: str | None
    data: dict
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get(
    "/notifications",
    response_model=ListResponse[NotificationResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_notifications(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List unread notifications for the current user."""
    svc = NotificationService(db)
    notifications, total = await svc.list_unread(user.id, page, per_page)
    return ListResponse(
        data=[NotificationResponse.model_validate(n) for n in notifications],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.put(
    "/notifications/{notification_id}/read",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def mark_notification_read(
    notification_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a single notification as read."""
    svc = NotificationService(db)
    await svc.mark_read(notification_id, user.id)
    await db.commit()
    return DataResponse(data={"status": "ok"})


@router.put(
    "/notifications/read-all",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def mark_all_notifications_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all unread notifications as read for the current user."""
    svc = NotificationService(db)
    count = await svc.mark_all_read(user.id)
    await db.commit()
    return DataResponse(data={"marked_read": count})

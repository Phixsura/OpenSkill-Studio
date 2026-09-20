"""Notification API — in-app notification management.

All endpoints require authentication. Users can only access their own
notifications and preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.notification import (
    NotificationPreferenceResponse,
    NotificationResponse,
    UnreadCountResponse,
    UpdatePreferencesRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Notifications"])


@router.get(
    "/notifications",
    response_model=CursorListResponse[NotificationResponse],
)
async def list_notifications(
    unread_only: bool = Query(False),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List notifications for the current user, newest first."""
    from app.talent.services.notifications import TalentNotificationService

    svc = TalentNotificationService(db)
    items, has_more = await svc.list_notifications(
        user.id, unread_only=unread_only, cursor=cursor, limit=limit
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[NotificationResponse.model_validate(n) for n in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/notifications/unread-count",
    response_model=DataResponse[UnreadCountResponse],
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get unread notification count for badge display."""
    from app.talent.services.notifications import TalentNotificationService

    svc = TalentNotificationService(db)
    count = await svc.get_unread_count(user.id)
    return DataResponse(data=UnreadCountResponse(count=count))


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=DataResponse[NotificationResponse],
)
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    from app.talent.services.notifications import TalentNotificationService

    svc = TalentNotificationService(db)
    notif = await svc.mark_read(notification_id, user.id)
    if not notif:
        raise HTTPException(404, "Notification not found")
    await db.commit()
    await db.refresh(notif)
    return DataResponse(data=NotificationResponse.model_validate(notif))


@router.post("/notifications/mark-all-read", response_model=DataResponse[dict])
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark all unread notifications as read."""
    from app.talent.services.notifications import TalentNotificationService

    svc = TalentNotificationService(db)
    count = await svc.mark_all_read(user.id)
    await db.commit()
    return DataResponse(data={"marked_read": count})


@router.get(
    "/notifications/preferences",
    response_model=DataResponse[list[NotificationPreferenceResponse]],
)
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get notification preferences with defaults for missing types."""
    from app.talent.services.notifications import TalentNotificationService

    svc = TalentNotificationService(db)
    prefs = await svc.get_preferences(user.id)
    return DataResponse(data=[NotificationPreferenceResponse(**p) for p in prefs])


@router.put(
    "/notifications/preferences",
    response_model=DataResponse[list[NotificationPreferenceResponse]],
)
async def update_preferences(
    body: UpdatePreferencesRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update notification preferences."""
    from app.talent.services.notifications import TalentNotificationService

    svc = TalentNotificationService(db)
    try:
        prefs = await svc.update_preferences(user.id, body.preferences)
    except ValueError:
        raise HTTPException(422, "Validation error") from None
    await db.commit()
    return DataResponse(data=[NotificationPreferenceResponse(**p) for p in prefs])

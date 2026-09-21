"""Activity log API — user timeline and org audit trail.

Authorization:
  - My activity: authenticated user (own timeline)
  - Org activity: org member (admin audit trail)
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

# NOTE: GET endpoints could benefit from Cache-Control: no-cache or ETag headers
router = APIRouter(prefix="/talent", tags=["Talent — Activity"])


class ActivityResponse(BaseModel):
    id: str
    user_id: str
    action_type: str
    target_type: str
    target_id: str
    extra: dict = Field(default_factory=dict, validation_alias="extra")
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/activity",
    response_model=CursorListResponse[ActivityResponse],
    summary="List My Activity",
)
async def list_my_activity(
    action_type: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List my activity timeline, newest first."""
    from app.talent.services.activity_log import ActivityLogService

    svc = ActivityLogService(db)
    items, has_more = await svc.list_activities(
        user.id, action_type=action_type, cursor=cursor, limit=limit
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[ActivityResponse.model_validate(a) for a in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/activity/org/{org_id}",
    response_model=CursorListResponse[ActivityResponse],
    summary="List Org Activity",
)
async def list_org_activity(
    org_id: str,
    action_type: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List organization activity audit trail — org members only."""
    await require_org_member(org_id, user, db)

    from app.talent.services.activity_log import ActivityLogService

    svc = ActivityLogService(db)
    items, has_more = await svc.list_org_activities(
        org_id, action_type=action_type, cursor=cursor, limit=limit
    )
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[ActivityResponse.model_validate(a) for a in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )

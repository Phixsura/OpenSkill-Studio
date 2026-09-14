"""In-app messaging API."""
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.application import Application
from app.talent.models.employer import Opportunity
from app.talent.models.message import ApplicationMessage
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Messaging"])

@router.post("/applications/{app_id}/messages", response_model=DataResponse[dict], status_code=201)
async def send_message(app_id: str, body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    is_candidate = app.user_id == user.id
    if not is_candidate:
        opp = await db.get(Opportunity, app.opportunity_id)
        if opp:
            await require_org_member(opp.employer_org_id, user, db)
    msg = ApplicationMessage(application_id=app_id, sender_id=user.id, sender_role="candidate" if is_candidate else "employer", message_type=body.get("message_type", "text"), content=body.get("content", ""))
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return DataResponse(data={"id": msg.id, "sender_role": msg.sender_role, "content": msg.content})

@router.get("/applications/{app_id}/messages", response_model=CursorListResponse[dict])
async def list_messages(app_id: str, cursor: str | None = Query(None), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    q = select(ApplicationMessage).where(ApplicationMessage.application_id == app_id)
    if cursor:
        q = q.where(ApplicationMessage.id < cursor)
    q = q.order_by(ApplicationMessage.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    nc = items[-1].id if has_more and items else None
    return CursorListResponse(data=[{"id": m.id, "sender_id": m.sender_id, "sender_role": m.sender_role, "content": m.content, "message_type": m.message_type, "read_at": m.read_at.isoformat() if m.read_at else None} for m in items], meta=CursorMeta(next_cursor=nc, has_more=has_more))

@router.patch("/messages/{msg_id}/read", response_model=DataResponse[dict])
async def mark_message_read(msg_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    msg = await db.get(ApplicationMessage, msg_id)
    if not msg:
        raise HTTPException(404, "Message not found")
    msg.read_at = datetime.now(UTC)
    await db.commit()
    return DataResponse(data={"id": msg.id, "read_at": msg.read_at.isoformat()})

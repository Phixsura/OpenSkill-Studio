"""Webhook endpoint management API."""
import secrets
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.webhook_endpoint import WebhookDeliveryLog, WebhookEndpointConfig
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Webhooks"])

@router.post("/orgs/{org_id}/webhooks", response_model=DataResponse[dict], status_code=201)
async def register_webhook(org_id: str, body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await require_org_member(org_id, user, db)
    url = body.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        raise HTTPException(422, "Webhook URL must use HTTPS")
    if not parsed.hostname or parsed.hostname in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        raise HTTPException(422, "Webhook URL must not point to localhost or private addresses")
    ep = WebhookEndpointConfig(org_id=org_id, url=url, secret=secrets.token_urlsafe(32), event_types=body.get("event_types", []), created_by=user.id)
    db.add(ep)
    await db.commit()
    await db.refresh(ep)
    return DataResponse(data={"id": ep.id, "url": ep.url, "secret": ep.secret, "event_types": ep.event_types})

@router.get("/orgs/{org_id}/webhooks", response_model=CursorListResponse[dict])
async def list_webhooks(org_id: str, cursor: str | None = Query(None), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await require_org_member(org_id, user, db)
    q = select(WebhookEndpointConfig).where(WebhookEndpointConfig.org_id == org_id)
    if cursor:
        q = q.where(WebhookEndpointConfig.id < cursor)
    q = q.order_by(WebhookEndpointConfig.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    nc = items[-1].id if has_more and items else None
    return CursorListResponse(data=[{"id": e.id, "url": e.url, "active": e.active, "event_types": e.event_types} for e in items], meta=CursorMeta(next_cursor=nc, has_more=has_more))

@router.delete("/webhooks/{endpoint_id}", response_model=DataResponse[dict])
async def delete_webhook(endpoint_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    ep = await db.get(WebhookEndpointConfig, endpoint_id)
    if not ep:
        raise HTTPException(404, "Webhook endpoint not found")
    await require_org_member(ep.org_id, user, db)
    await db.delete(ep)
    await db.commit()
    return DataResponse(data={"deleted": True})

@router.get("/webhooks/{endpoint_id}/deliveries", response_model=CursorListResponse[dict])
async def list_deliveries(endpoint_id: str, cursor: str | None = Query(None), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # Authorization: must be org member of the webhook's org
    ep = await db.get(WebhookEndpointConfig, endpoint_id)
    if not ep:
        raise HTTPException(404, "Webhook endpoint not found")
    await require_org_member(ep.org_id, user, db)
    q = select(WebhookDeliveryLog).where(WebhookDeliveryLog.endpoint_id == endpoint_id)
    if cursor:
        q = q.where(WebhookDeliveryLog.id < cursor)
    q = q.order_by(WebhookDeliveryLog.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    nc = items[-1].id if has_more and items else None
    return CursorListResponse(data=[{"id": d.id, "event_type": d.event_type, "status": d.status, "response_code": d.response_code, "attempts": d.attempts} for d in items], meta=CursorMeta(next_cursor=nc, has_more=has_more))

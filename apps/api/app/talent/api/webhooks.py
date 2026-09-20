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

# NOTE: Webhook secret rotation: delete + re-register with new secret.
# Dedicated rotate endpoint is planned.

router = APIRouter(prefix="/talent", tags=["Talent — Webhooks"])


@router.post("/orgs/{org_id}/webhooks", response_model=DataResponse[dict], status_code=201,
    summary="Register Webhook",
)
async def register_webhook(
    org_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register webhook."""
    await require_org_member(org_id, user, db)
    url = body.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        raise HTTPException(422, "Webhook URL must use HTTPS")
    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        raise HTTPException(422, "Invalid webhook URL")
    # Resolve hostname and reject private/loopback/link-local/reserved IPs
    import ipaddress
    import socket

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise HTTPException(422, "Cannot resolve webhook hostname")  # noqa: B904
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise HTTPException(422, "Webhook URL resolves to a disallowed address")
    ep = WebhookEndpointConfig(
        org_id=org_id,
        url=url,
        secret=secrets.token_urlsafe(32),
        event_types=body.get("event_types", []),
        created_by=user.id,
    )
    db.add(ep)
    await db.commit()
    await db.refresh(ep)
    return DataResponse(
        data={
            "id": ep.id,
            "url": ep.url,
            "secret": ep.secret,
            "event_types": ep.event_types,
            "note": "Save this secret — it will not be shown again",
        }
    )


@router.get("/orgs/{org_id}/webhooks", response_model=CursorListResponse[dict],
    summary="List Webhooks",
)
async def list_webhooks(
    org_id: str,
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List webhooks."""
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
    return CursorListResponse(
        data=[
            {
                "id": e.id,
                "url": e.url,
                "active": e.active,
                "event_types": e.event_types,
                "secret_prefix": e.secret[:8] + "..." if e.secret else None,
            }
            for e in items
        ],
        meta=CursorMeta(next_cursor=nc, has_more=has_more),
    )


@router.delete("/webhooks/{endpoint_id}", response_model=DataResponse[dict],
    summary="Delete Webhook",
)
async def delete_webhook(
    endpoint_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """Delete webhook."""
    ep = await db.get(WebhookEndpointConfig, endpoint_id)
    if not ep:
        raise HTTPException(404, "Webhook endpoint not found")
    await require_org_member(ep.org_id, user, db)
    await db.delete(ep)
    await db.commit()
    return DataResponse(data={"deleted": True})


@router.get("/webhooks/{endpoint_id}/deliveries", response_model=CursorListResponse[dict],
    summary="List Deliveries",
)
async def list_deliveries(
    endpoint_id: str,
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List deliveries."""
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
    return CursorListResponse(
        data=[
            {
                "id": d.id,
                "event_type": d.event_type,
                "status": d.status,
                "response_code": d.response_code,
                "attempts": d.attempts,
            }
            for d in items
        ],
        meta=CursorMeta(next_cursor=nc, has_more=has_more),
    )

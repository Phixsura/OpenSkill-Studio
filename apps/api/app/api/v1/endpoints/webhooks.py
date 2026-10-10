"""Webhook subscription management endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, reject_ctrl_str
from app.services.webhook import MAX_EVENTS_PER_WEBHOOK, VALID_EVENT_TYPES, WebhookService

router = APIRouter(tags=["Webhooks"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


class CreateWebhookRequest(BaseModel):
    url: str
    events: list[str] = []

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        # R88e: a NUL in the URL *path* passes the prefix/length checks and the
        # SSRF host gate (host is clean), then 500s on the VARCHAR write; other
        # C0 chars would store raw. Reject the whole control range up front.
        reject_ctrl_str(v, "url")
        v = v.strip()
        if not v.startswith(("https://", "http://")):
            raise ValueError("URL must start with https:// or http://")
        if len(v) > 500:
            raise ValueError("URL must be 500 characters or less")
        return v

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: list[str]) -> list[str]:
        # Defect #104: an empty list used to create a subscription that the
        # delivery path's falsy guard treats as receive-EVERYTHING — an
        # accidental wildcard. Empty means none, not all: reject it.
        if not v:
            raise ValueError("events must list at least one event type")
        if len(v) > MAX_EVENTS_PER_WEBHOOK:
            raise ValueError(f"Maximum {MAX_EVENTS_PER_WEBHOOK} events per webhook")
        # Marathon R15 (E2E-caught): this SCHEMA validator duplicated the
        # service check and silently missed the R7 mesh-pattern arm — the
        # live API rejected com.openskill.* subscriptions that service-level
        # tests accepted. Keep both layers in lockstep via the shared regex.
        from app.services.webhook import _MESH_PATTERN_RE

        for event in v:
            if event in VALID_EVENT_TYPES or _MESH_PATTERN_RE.fullmatch(event):
                continue
            raise ValueError(
                f"Unknown event type: {event}. Valid: a com.openskill.* mesh "
                f"pattern or one of: {', '.join(sorted(VALID_EVENT_TYPES))}"
            )
        return v


class WebhookCreatedResponse(BaseModel):
    """Response for webhook creation — includes the secret (shown only once)."""

    id: str
    org_id: str
    url: str
    events: list
    secret: str
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookResponse(BaseModel):
    """Response for webhook list/detail — secret is masked."""

    id: str
    org_id: str
    url: str
    events: list
    secret: str  # will be masked
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("secret")
    @classmethod
    def mask_secret(cls, v: str) -> str:
        if len(v) > 8:
            return v[:4] + "****" + v[-4:]
        return "****"


@router.post(
    "/orgs/{org_id}/webhooks",
    response_model=DataResponse[WebhookCreatedResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_webhook(
    org_id: str,
    body: CreateWebhookRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    # Issue #27: webhooks are a plan entitlement
    from app.controlplane import facade as cp_facade

    tenant = await cp_facade.get_tenant_for_org(db, org_id)
    await cp_facade.require_feature(db, tenant, "webhooks")
    svc = WebhookService(db)
    sub = await svc.create(org_id, body.url, body.events, actor_user_id=user.id)
    await db.commit()
    return DataResponse(data=WebhookCreatedResponse.model_validate(sub))


@router.get(
    "/orgs/{org_id}/webhooks",
    response_model=DataResponse[list[WebhookResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_webhooks(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WebhookService(db)
    subs = await svc.list_subscriptions(org_id)
    return DataResponse(data=[WebhookResponse.model_validate(s) for s in subs])


@router.post(
    "/orgs/{org_id}/webhooks/{webhook_id}/rotate-secret",
    response_model=DataResponse[WebhookCreatedResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def rotate_webhook_secret(
    org_id: str,
    webhook_id: str,
    immediate: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Defect #103: rotate the signing secret in place — the new secret is
    returned once. Default rotation keeps the old secret co-signing mesh
    deliveries for 7 days (ADR-018 §12.2); ?immediate=true is the
    leaked-secret path (old key stops signing now)."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WebhookService(db)
    sub = await svc.rotate_secret(
        webhook_id, org_id, actor_user_id=user.id, immediate=immediate
    )
    await db.commit()
    return DataResponse(data=WebhookCreatedResponse.model_validate(sub))


@router.post(
    "/orgs/{org_id}/webhooks/{webhook_id}/test",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def test_webhook(
    org_id: str,
    webhook_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """R37 (Svix 'send example' parity): synchronously dispatch a sample
    SIGNED CloudEvent to the endpoint and report status/latency — verifies
    connectivity and lets the receiver check its signature code without
    waiting for a real event. Never touches the delivery log."""
    import json as _json
    import time as _time
    from datetime import UTC, datetime

    from ulid import ULID

    from app.integrations.security import EgressBlockedError, EgressClient
    from app.integrations.services.events import build_delivery_headers

    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WebhookService(db)
    subs = {s.id: s for s in await svc.list_subscriptions(org_id)}
    sub = subs.get(webhook_id)
    if sub is None:
        raise AppError("WEBHOOK_NOT_FOUND", "Webhook not found", 404)
    now = datetime.now(UTC)
    event_id = str(ULID())
    body = _json.dumps(
        {
            "specversion": "1.0",
            "id": event_id,
            "source": f"/orgs/{org_id}",
            "type": "com.openskill.integration.subscription.test.v1",
            "subject": sub.id,
            "time": now.isoformat(),
            "datacontenttype": "application/json",
            "data": {"test": True, "subscription_id": sub.id},
        },
        separators=(",", ":"),
    ).encode()
    headers = build_delivery_headers(sub, event_id, body, now)
    started = _time.monotonic()
    try:
        resp = await EgressClient().request("POST", sub.url, headers=headers, content=body)
        result = {
            "delivered": 200 <= resp.status_code < 300,
            "status_code": resp.status_code,
            "latency_ms": int((_time.monotonic() - started) * 1000),
            "error": None,
        }
    except EgressBlockedError as exc:
        result = {"delivered": False, "status_code": None, "latency_ms": None,
                  "error": exc.message}
    except Exception as exc:  # connection refused / timeout — a result, not a 500
        result = {
            "delivered": False,
            "status_code": None,
            "latency_ms": int((_time.monotonic() - started) * 1000),
            "error": type(exc).__name__,
        }
    return DataResponse(data=result)


@router.delete(
    "/orgs/{org_id}/webhooks/{webhook_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_webhook(
    org_id: str,
    webhook_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WebhookService(db)
    await svc.delete(webhook_id, org_id, actor_user_id=user.id)
    await db.commit()

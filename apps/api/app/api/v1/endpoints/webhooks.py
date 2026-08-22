"""Webhook subscription management endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.services.webhook import MAX_EVENTS_PER_WEBHOOK, VALID_EVENT_TYPES, WebhookService

router = APIRouter(tags=["Webhooks"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


class CreateWebhookRequest(BaseModel):
    url: str
    events: list[str] = []

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("https://", "http://")):
            raise ValueError("URL must start with https:// or http://")
        if len(v) > 500:
            raise ValueError("URL must be 500 characters or less")
        return v

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_EVENTS_PER_WEBHOOK:
            raise ValueError(f"Maximum {MAX_EVENTS_PER_WEBHOOK} events per webhook")
        for event in v:
            if event not in VALID_EVENT_TYPES:
                raise ValueError(
                    f"Unknown event type: {event}. "
                    f"Valid types: {', '.join(sorted(VALID_EVENT_TYPES))}"
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
    svc = WebhookService(db)
    sub = await svc.create(org_id, body.url, body.events)
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
    await svc.delete(webhook_id, org_id)
    await db.commit()

"""Event mesh admin endpoints: browse events, delivery log, replay (§15)."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.exceptions import AppError
from app.integrations.models import DeliveryAttempt, EventDelivery, IntegrationEvent
from app.integrations.services.events import replay_delivery
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])


class EventResponse(BaseModel):
    id: str
    type: str
    source: str
    subject: str | None
    time: datetime | None
    data: dict


class AttemptResponse(BaseModel):
    id: str
    status_code: int | None
    error: str | None
    latency_ms: int | None
    attempted_at: datetime


class DeliveryResponse(BaseModel):
    id: str
    event_id: str
    event_type: str
    subscription_id: str
    status: str
    attempt_count: int
    next_attempt_at: datetime | None
    replay_of: str | None
    created_at: datetime
    attempts: list[AttemptResponse] | None = None


async def _admin(org_id: str, user: User, db: AsyncSession) -> None:
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)


@router.get("/events", response_model=DataResponse[list[EventResponse]])
async def list_events(
    org_id: str,
    type_prefix: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    q = (
        select(IntegrationEvent)
        .where(IntegrationEvent.org_id == org_id)
        .order_by(IntegrationEvent.time.desc())
        .limit(limit)
    )
    if type_prefix:
        from app.ecosystem.security import escape_like

        q = q.where(IntegrationEvent.type.like(f"{escape_like(type_prefix)}%", escape="\\"))
    events = (await db.execute(q)).scalars().all()
    return {"data": [EventResponse.model_validate(e, from_attributes=True) for e in events]}


def _delivery_response(
    d: EventDelivery, event_type: str, attempts: list[DeliveryAttempt] | None = None
) -> DeliveryResponse:
    return DeliveryResponse(
        id=d.id,
        event_id=d.event_id,
        event_type=event_type,
        subscription_id=d.subscription_id,
        status=d.status,
        attempt_count=d.attempt_count,
        next_attempt_at=d.next_attempt_at,
        replay_of=d.replay_of,
        created_at=d.created_at,
        attempts=(
            [AttemptResponse.model_validate(a, from_attributes=True) for a in attempts]
            if attempts is not None
            else None
        ),
    )


@router.get("/deliveries", response_model=DataResponse[list[DeliveryResponse]])
async def list_deliveries(
    org_id: str,
    status: str | None = Query(default=None, max_length=20),
    subscription_id: str | None = Query(default=None, max_length=26),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    q = (
        select(EventDelivery, IntegrationEvent.type)
        .join(IntegrationEvent, IntegrationEvent.id == EventDelivery.event_id)
        .where(IntegrationEvent.org_id == org_id)
        .order_by(EventDelivery.created_at.desc())
        .limit(limit)
    )
    if status:
        q = q.where(EventDelivery.status == status)
    if subscription_id:
        q = q.where(EventDelivery.subscription_id == subscription_id)
    rows = (await db.execute(q)).all()
    return {"data": [_delivery_response(d, t) for d, t in rows]}


@router.get("/deliveries/{delivery_id}", response_model=DataResponse[DeliveryResponse])
async def get_delivery(
    org_id: str,
    delivery_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    delivery = await db.get(EventDelivery, delivery_id)
    event = await db.get(IntegrationEvent, delivery.event_id) if delivery else None
    if delivery is None or event is None or event.org_id != org_id:
        raise AppError("DELIVERY_NOT_FOUND", "Delivery not found", 404)
    attempts = (
        (
            await db.execute(
                select(DeliveryAttempt)
                .where(DeliveryAttempt.delivery_id == delivery.id)
                .order_by(DeliveryAttempt.attempted_at.asc())
            )
        )
        .scalars()
        .all()
    )
    return {"data": _delivery_response(delivery, event.type, list(attempts))}


@router.post("/deliveries/{delivery_id}/replay", response_model=DataResponse[DeliveryResponse])
async def replay(
    org_id: str,
    delivery_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    clone = await replay_delivery(db, org_id, delivery_id)
    event = await db.get(IntegrationEvent, clone.event_id)
    resp = _delivery_response(clone, event.type if event else "?")
    await db.commit()
    return {"data": resp}

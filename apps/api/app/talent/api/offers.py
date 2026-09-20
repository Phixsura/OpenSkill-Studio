from app.talent.schemas.requests import AnalyticsBody

"""Offer management API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.application import Application
from app.talent.models.employer import Opportunity
from app.talent.models.offer import Offer
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Offers"])


@router.post(
    "/applications/{app_id}/offer",
    response_model=DataResponse[dict],
    status_code=201,
    summary="Create Offer",
)
async def create_offer(
    app_id: str,
    body: AnalyticsBody,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    opp = await db.get(Opportunity, app.opportunity_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    await require_org_member(opp.employer_org_id, user, db)
    offer = Offer(
        application_id=app_id,
        employer_org_id=opp.employer_org_id,
        role_title=body.get("role_title", opp.title),
        compensation_text=body.get("compensation_text"),
        conditions=body.get("conditions", []),
        custom_sections=body.get("custom_sections", []),
        created_by=user.id,
    )
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    return DataResponse(
        data={"id": offer.id, "status": offer.status, "role_title": offer.role_title}
    )


@router.get(
    "/offers",
    response_model=CursorListResponse[dict],
    summary="List Offers",
)
async def list_offers(
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = (
        select(Offer)
        .join(Application, Application.id == Offer.application_id)
        .where(Application.user_id == user.id)
    )
    if cursor:
        q = q.where(Offer.id < cursor)
    q = q.order_by(Offer.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[
            {
                "id": o.id,
                "role_title": o.role_title,
                "status": o.status,
                "compensation_text": o.compensation_text,
            }
            for o in items
        ],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.patch(
    "/offers/{offer_id}/accept",
    response_model=DataResponse[dict],
    summary="Accept Offer",
)
async def accept_offer(
    offer_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    offer = await db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    app = await db.get(Application, offer.application_id)
    if not app or app.user_id != user.id:
        raise HTTPException(404, "Offer not found")
    from app.talent.services.offer_management import OFFER_TRANSITIONS

    if "accepted" not in OFFER_TRANSITIONS.get(offer.status, set()):
        raise HTTPException(422, f"Cannot accept offer in status '{offer.status}'")
    from datetime import UTC, datetime

    offer.status = "accepted"
    offer.accepted_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(offer)
    return DataResponse(data={"id": offer.id, "status": offer.status})


@router.patch(
    "/offers/{offer_id}/decline",
    response_model=DataResponse[dict],
    summary="Decline Offer",
)
async def decline_offer(
    offer_id: str,
    body: AnalyticsBody | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    offer = await db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    app = await db.get(Application, offer.application_id)
    if not app or app.user_id != user.id:
        raise HTTPException(404, "Offer not found")
    from app.talent.services.offer_management import OFFER_TRANSITIONS

    if "declined" not in OFFER_TRANSITIONS.get(offer.status, set()):
        raise HTTPException(422, f"Cannot decline offer in status '{offer.status}'")
    from datetime import UTC, datetime

    offer.status = "declined"
    offer.declined_at = datetime.now(UTC)
    offer.decline_reason = (body or {}).get("reason")
    await db.commit()
    await db.refresh(offer)
    return DataResponse(data={"id": offer.id, "status": offer.status})

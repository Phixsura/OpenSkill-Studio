"""Pricing & availability intelligence endpoints (Part E)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.schemas import (
    AvailabilityResponse,
    PriceObservationResponse,
    ReconcilePriceRequest,
)
from app.ecosystem.services.pricing import AvailabilityService, PricingService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/pricing", tags=["Ecosystem — Pricing"])


@router.get("/observations", response_model=DataResponse[list[PriceObservationResponse]])
async def list_price_observations(
    entity_kind: str | None = None,
    entity_id: str | None = None,
    reconciliation_status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = await PricingService(db).list(
        entity_kind=entity_kind,
        entity_id=entity_id,
        reconciliation_status=reconciliation_status,
        limit=limit,
        offset=offset,
    )
    return {"data": rows}


@router.post(
    "/observations/extract/{observation_id}",
    response_model=DataResponse[list[PriceObservationResponse]],
    status_code=201,
)
async def extract_prices(
    observation_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    rows = await PricingService(db).extract_from_observation(observation_id)
    await db.commit()
    return {"data": rows}


@router.post(
    "/observations/{price_obs_id}/reconcile",
    response_model=DataResponse[PriceObservationResponse],
)
async def reconcile_price(
    price_obs_id: str,
    body: ReconcilePriceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    row = await PricingService(db).reconcile(
        price_obs_id,
        decision=body.decision,
        actor_id=user.id,
        provider_key=body.provider_key,
        model_or_service=body.model_or_service,
    )
    await db.commit()
    return {"data": row}


@router.get("/availability", response_model=DataResponse[list[AvailabilityResponse]])
async def list_availability(
    entity_kind: str | None = None,
    entity_id: str | None = None,
    record_type: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = await AvailabilityService(db).list(
        entity_kind=entity_kind, entity_id=entity_id, record_type=record_type, limit=limit
    )
    return {"data": rows}

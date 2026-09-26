"""Pricing & availability intelligence endpoints (Part E)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import eco_audit, require_platform_admin
from app.ecosystem.schemas import (
    AvailabilityResponse,
    EstimateRequest,
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
    await eco_audit(
        db, user, action="eco.price_reconciled", target_type="eco_price_observation",
        target_id=price_obs_id,
        after={"decision": body.decision, "cost_rate_id": row.approved_cost_rate_id},
    )
    await db.commit()
    return {"data": row}


@router.post(
    "/availability/probe/{entity_kind}/{entity_id}",
    response_model=DataResponse[AvailabilityResponse],
    status_code=201,
)
async def probe_availability(
    entity_kind: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """§11.3: on-demand status probe, independent of catalog syncs."""
    record = await AvailabilityService(db).probe_status(entity_kind, entity_id)
    await db.commit()
    return {"data": record}


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

@router.post("/estimate", response_model=DataResponse[list])
async def estimate_workload_cost(
    payload: EstimateRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Advisory workload cost estimate against latest observed/approved prices.

    Sorted fully-priced-then-cheapest; unpriced units are flagged, never
    silently zeroed. This is NOT a billing quote (ADR-016 safety posture).
    """
    rows = await PricingService(db).estimate(
        entity_kind=payload.entity_kind,
        entity_ids=payload.entity_ids,
        workload=payload.workload,
    )
    return {"data": rows}

@router.get("/availability/uptime", response_model=DataResponse[dict])
async def availability_uptime(
    entity_kind: str = Query(...),
    entity_id: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Time-weighted uptime/SLO summary from our own probe history (honest
    'unknown' before first probe; coverage_pct exposes observation gaps)."""
    out = await AvailabilityService(db).uptime(
        entity_kind=entity_kind, entity_id=entity_id, days=days
    )
    return {"data": out}

@router.get("/history", response_model=DataResponse[dict])
async def price_history(
    entity_kind: str = Query(...),
    entity_id: str = Query(...),
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Per-unit price time series + linear trend (advisory projection)."""
    out = await PricingService(db).history(
        entity_kind=entity_kind, entity_id=entity_id, unit=unit
    )
    return {"data": out}


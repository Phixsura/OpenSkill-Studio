"""Operator workspace + approved-signal endpoints (Parts N, O, P)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.schemas import ChangeEventResponse
from app.ecosystem.services.dashboard import DashboardService
from app.ecosystem.services.signals import SignalsService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem — Dashboard & Signals"])


@router.get("/dashboard", response_model=DataResponse[dict])
async def dashboard_overview(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await DashboardService(db).overview()}


@router.get("/dashboard/change-feed", response_model=DataResponse[list[ChangeEventResponse]])
async def change_feed(
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {
        "data": await DashboardService(db).change_feed(
            severity=severity, limit=limit, offset=offset
        )
    }


@router.get("/signals/matching", response_model=DataResponse[list])
async def matching_signals(
    capability_key: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Approved-only intelligence signals (Part N). Raw observations never leak."""
    return {"data": await SignalsService(db).matching_signals(capability_key=capability_key)}


@router.get("/signals/workforce", response_model=DataResponse[list])
async def workforce_signals(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Emerging/obsolete capability planning signals (Part O). Advisory only."""
    return {"data": await SignalsService(db).workforce_signals()}


@router.get("/registry-badges", response_model=DataResponse[dict])
async def registry_badges(
    refs: str = Query(..., description="Comma-separated kind:id pairs"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    entity_refs = []
    for pair in refs.split(",")[:50]:
        if ":" in pair:
            kind, _, entity_id = pair.strip().partition(":")
            entity_refs.append((kind, entity_id))
    return {"data": await SignalsService(db).registry_badges(entity_refs=entity_refs)}

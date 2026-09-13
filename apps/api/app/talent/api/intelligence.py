"""Workforce intelligence API — demand, supply, gaps, coverage, analytics.

All aggregates enforce privacy minimum thresholds.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.services.workforce import WorkforceIntelligenceService

router = APIRouter(prefix="/talent/intelligence", tags=["Talent — Intelligence"])


@router.get("/demand", response_model=DataResponse[list[dict]])
async def get_demand(
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Demand by capability (aggregated, privacy-safe)."""
    svc = WorkforceIntelligenceService(db)
    signals = await svc.get_demand_signals(category=category, limit=limit)
    return DataResponse(data=[
        {
            "capability_id": s.capability_id,
            "capability_name": s.capability_name,
            "category": s.category,
            "open_opportunities": s.open_opportunities,
            "total_demand": s.total_demand,
        }
        for s in signals
    ])


@router.get("/supply", response_model=DataResponse[list[dict]])
async def get_supply(
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Verified supply by capability (aggregated, privacy-safe)."""
    svc = WorkforceIntelligenceService(db)
    signals = await svc.get_supply_signals(category=category, limit=limit)
    return DataResponse(data=[
        {
            "capability_id": s.capability_id,
            "capability_name": s.capability_name,
            "category": s.category,
            "total_supply": s.total_supply,
        }
        for s in signals
    ])


@router.get("/gaps", response_model=DataResponse[list[dict]])
async def get_gaps(
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Demand-supply gap analysis (aggregated, privacy-safe)."""
    svc = WorkforceIntelligenceService(db)
    gaps = await svc.get_gap_analysis(category=category, limit=limit)
    return DataResponse(data=[
        {
            "capability_id": g.capability_id,
            "capability_name": g.capability_name,
            "demand_count": g.demand_count,
            "qualified_supply": g.qualified_supply,
            "gap": g.gap,
            "gap_severity": g.gap_severity,
            "content_coverage": g.content_coverage,
        }
        for g in gaps
    ])


@router.get("/coverage", response_model=DataResponse[list[dict]])
async def get_coverage(
    capability_id: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Curriculum coverage matrix."""
    svc = WorkforceIntelligenceService(db)
    return DataResponse(
        data=await svc.get_coverage_matrix(capability_id=capability_id, limit=limit)
    )


@router.get("/placements", response_model=DataResponse[dict])
async def get_placement_analytics(
    employer_org_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Placement funnel analytics."""
    if employer_org_id:
        await require_org_member(employer_org_id, user, db)
    svc = WorkforceIntelligenceService(db)
    return DataResponse(
        data=await svc.get_placement_analytics(employer_org_id=employer_org_id)
    )

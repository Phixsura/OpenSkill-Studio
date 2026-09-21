"""Analytics dashboard API endpoints — school, employer, platform (§40–§42)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User, UserRole
from app.schemas.base import DataResponse
from app.talent.services.dashboards import (
    EmployerDashboardService,
    PlatformDashboardService,
    SchoolDashboardService,
)

router = APIRouter(prefix="/talent/dashboards", tags=["Talent — Dashboards"])


@router.get(
    "/school",
    response_model=DataResponse[dict],
    summary="Get School Dashboard",
)
async def get_school_dashboard(
    org_id: str = Query(..., description="School org ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """School/training-provider analytics dashboard (§40).

    Includes capability distribution, assessment pass rates, placement
    stats, and employer feedback summary. All aggregates privacy-safe.
    """
    await require_org_member(org_id, user, db)
    svc = SchoolDashboardService(db)
    return DataResponse(data=await svc.get_dashboard(org_id))


@router.get(
    "/employer",
    response_model=DataResponse[dict],
    summary="Get Employer Dashboard",
)
async def get_employer_dashboard(
    org_id: str = Query(..., description="Employer org ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Employer analytics dashboard (§41).

    Includes open opportunities, application pipeline, active placements,
    and time-to-fill metrics.
    """
    await require_org_member(org_id, user, db)
    svc = EmployerDashboardService(db)
    return DataResponse(data=await svc.get_dashboard(org_id))


@router.get(
    "/platform",
    response_model=DataResponse[dict],
    summary="Get Platform Dashboard",
)
async def get_platform_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Platform workforce dashboard (§42). Platform admin only.

    Includes global capability count, open opportunities, active
    placements, credential adoption, and evidence volume.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Only platform admins can view the platform dashboard")
    svc = PlatformDashboardService(db)
    return DataResponse(data=await svc.get_dashboard())

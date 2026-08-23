"""Gamification endpoints — leaderboard and user points."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse
from app.services.gamification import GamificationService

router = APIRouter(tags=["Gamification"])


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    display_name: str
    total_points: int
    level: int


class UserPointsResponse(BaseModel):
    total_points: int
    level: int


class PointsHistoryEntry(BaseModel):
    id: str
    points: int
    reason: str
    reference_id: str | None
    description: str | None
    created_at: str | None


@router.get(
    "/orgs/{org_id}/leaderboard",
    response_model=DataResponse[list[LeaderboardEntry]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def get_leaderboard(
    org_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Top users by points in this org."""
    await require_org_member(org_id, user, db)
    svc = GamificationService(db)
    entries = await svc.get_leaderboard(org_id, limit)
    return DataResponse(data=[LeaderboardEntry(**e) for e in entries])


@router.get(
    "/orgs/{org_id}/points/me",
    response_model=DataResponse[UserPointsResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def get_my_points(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Current user's points and level."""
    await require_org_member(org_id, user, db)
    svc = GamificationService(db)
    data = await svc.get_user_points(user.id, org_id)
    return DataResponse(data=UserPointsResponse(**data))


@router.get(
    "/orgs/{org_id}/points/me/history",
    response_model=DataResponse[list[PointsHistoryEntry]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def get_my_points_history(
    org_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recent point awards for current user."""
    await require_org_member(org_id, user, db)
    svc = GamificationService(db)
    entries = await svc.get_user_points_history(user.id, org_id, limit)
    return DataResponse(data=[PointsHistoryEntry(**e) for e in entries])

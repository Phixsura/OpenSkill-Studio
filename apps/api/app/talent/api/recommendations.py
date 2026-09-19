"""Personalized recommendation feed API (N19)."""

import dataclasses

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/talent", tags=["Talent — Recommendations"])


@router.get("/recommendations/feed", response_model=DataResponse[list[dict]])
async def get_recommendation_feed(
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(None),
    opportunity_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Personalized opportunity recommendation feed.

    Combines capability match, type preference, career goal alignment,
    recency, and engagement signals to rank opportunities.
    Excludes already-applied opportunities.
    """
    from app.talent.services.recommendation_feed import RecommendationFeedService

    svc = RecommendationFeedService(db)
    results, has_more = await svc.get_feed(
        user.id,
        limit=limit,
        cursor=cursor,
        opportunity_type=opportunity_type,
    )
    return DataResponse(data=[dataclasses.asdict(r) for r in results])

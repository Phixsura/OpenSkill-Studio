"""Talent matching API — candidate↔opportunity explainable matching.

Authorization:
  - Employer-side (generate candidate shortlist): employer org member
  - Candidate-side (see matching opportunities): any authenticated user (own matches)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.employer import Opportunity

router = APIRouter(prefix="/talent", tags=["Talent — Matching"])


@router.post("/opportunities/{opp_id}/match", response_model=DataResponse[dict])
async def match_candidates(
    opp_id: str,
    limit: int = Query(20, ge=1, le=100),
    explain: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate candidate shortlist for an opportunity — employer only."""
    opp = await db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.talent_matching import TalentMatchingService

    svc = TalentMatchingService(db)
    results = await svc.match_candidates_for_opportunity(
        opportunity_id=opp_id,
        employer_org_id=opp.employer_org_id,
        user_id=user.id,
        limit=limit,
        explain=explain,
    )
    return DataResponse(data=results)


@router.get("/opportunities/matches", response_model=DataResponse[list[dict]])
async def match_opportunities_for_user(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Find matching opportunities for the current user."""
    from app.talent.services.talent_matching import TalentMatchingService

    svc = TalentMatchingService(db)
    results = await svc.match_opportunities_for_user(
        user_id=user.id,
        limit=limit,
    )
    return DataResponse(data=results)

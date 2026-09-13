"""Talent matching API — candidate↔opportunity explainable matching.

Authorization:
  - Employer-side (generate candidate shortlist): employer org member
  - Candidate-side (see matching opportunities): any authenticated user (own matches)
  - Fairness metrics: employer org member (same as match)
"""

import dataclasses

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.employer import Opportunity

router = APIRouter(prefix="/talent", tags=["Talent — Matching"])


@router.post("/opportunities/{opp_id}/match", response_model=DataResponse[list[dict]])
async def match_candidates(
    opp_id: str,
    limit: int = Query(20, ge=1, le=100),
    explain: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate candidate shortlist for an opportunity — employer only.

    Includes adjacent skill inference: candidates with related skills
    (via CapabilityEdge) earn partial credit instead of being excluded.
    """
    opp = await db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.talent_matching import TalentMatchingService

    svc = TalentMatchingService(db)
    results = await svc.match_candidates_for_opportunity(
        opportunity_id=opp_id,
        employer_org_id=opp.employer_org_id,
        limit=limit,
        explain=explain,
    )
    result_dicts = [dataclasses.asdict(r) for r in results]

    # Auto-compute fairness metrics
    from app.talent.services.fairness import FairnessService

    fairness_svc = FairnessService(db)
    fairness = await fairness_svc.compute_fairness_metrics(result_dicts)

    return DataResponse(data={
        "results": result_dicts,
        "fairness": fairness,
    })


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
    return DataResponse(data=[dataclasses.asdict(r) for r in results])


@router.get("/career-paths", response_model=DataResponse[list[dict]])
async def get_career_paths(
    limit: int = Query(10, ge=1, le=50),
    opportunity_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Predict reachable career paths for the current user.

    Finds opportunities 1-3 capability-gaps away and suggests
    specific learning actions to close each gap.
    """
    from app.talent.services.career_path import predict_career_paths

    include_types = [opportunity_type] if opportunity_type else None
    suggestions = await predict_career_paths(
        db,
        user.id,
        max_results=limit,
        include_types=include_types,
    )
    return DataResponse(data=[dataclasses.asdict(s) for s in suggestions])


@router.post("/opportunities/{opp_id}/match/fairness", response_model=DataResponse[dict])
async def get_match_fairness(
    opp_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Compute fairness metrics for an opportunity's candidate match.

    Runs the matching pipeline and returns only the fairness audit —
    useful for bias review without processing all candidate details.
    """
    opp = await db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.talent_matching import TalentMatchingService

    svc = TalentMatchingService(db)
    results = await svc.match_candidates_for_opportunity(
        opportunity_id=opp_id,
        employer_org_id=opp.employer_org_id,
        limit=limit,
    )

    from app.talent.services.fairness import FairnessService

    fairness_svc = FairnessService(db)
    result_dicts = [dataclasses.asdict(r) for r in results]
    fairness = await fairness_svc.compute_fairness_metrics(result_dicts)
    return DataResponse(data=fairness)

"""Replacement candidates endpoints (Part J)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.schemas import (
    DecisionRequest,
    GenerateCandidatesRequest,
    ReplacementCandidateResponse,
)
from app.ecosystem.services.replacement import ReplacementService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/replacements", tags=["Ecosystem — Replacements"])


@router.post("/candidates/generate", response_model=DataResponse[dict], status_code=201)
async def generate_candidates(
    body: GenerateCandidatesRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    compatible, incompatible = await ReplacementService(db).generate_candidates(
        deprecated_kind=body.deprecated_kind,
        deprecated_id=body.deprecated_id,
        weights=body.weights,
        limit=body.limit,
    )
    await db.commit()
    # Hard incompatibilities live in a SEPARATE list — never interleaved
    return {
        "data": {
            "ranked": [
                ReplacementCandidateResponse.model_validate(c).model_dump() for c in compatible
            ],
            "incompatible": [
                ReplacementCandidateResponse.model_validate(c).model_dump() for c in incompatible
            ],
        }
    }


@router.get("/candidates", response_model=DataResponse[list[ReplacementCandidateResponse]])
async def list_candidates(
    deprecated_kind: str | None = None,
    deprecated_id: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {
        "data": await ReplacementService(db).list_candidates(
            deprecated_kind=deprecated_kind,
            deprecated_id=deprecated_id,
            status=status,
            limit=limit,
        )
    }


@router.post(
    "/candidates/{candidate_id}/decide",
    response_model=DataResponse[ReplacementCandidateResponse],
)
async def decide_candidate(
    candidate_id: str,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    candidate = await ReplacementService(db).decide(
        candidate_id, decision=body.decision, actor_id=user.id
    )
    await db.commit()
    return {"data": candidate}

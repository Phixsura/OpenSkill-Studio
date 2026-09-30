"""Decision registry & promotion endpoints (ADR-017 §12, Parts J/K).

NOTE (route shadowing, §106.10): /experiments/decisions and
/experiments/promotion-drafts are static single-segment paths under
/experiments — this router must register BEFORE the dynamic
/experiments/{experiment_id} routes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.experiments.api.deps import check_enum, require_platform_admin
from app.experiments.models.decision import DECISIONS, PROMOTION_STATUSES
from app.experiments.schemas import (
    CreateDecisionRequest,
    CreatePromotionDraftRequest,
    DecisionRecordResponse,
    PromotionDraftResponse,
)
from app.experiments.security import EXPERIMENT_DOMAINS
from app.experiments.services.decisions import DecisionService
from app.experiments.services.promotion import PromotionService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/experiments", tags=["Experiments — Decisions"])


@router.get("/decisions", response_model=dict)
async def search_decisions(
    domain: str | None = None,
    decision: str | None = None,
    q: str | None = Query(default=None, max_length=200),
    cursor: str | None = Query(default=None, max_length=26),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    check_enum(domain, EXPERIMENT_DOMAINS, "domain")
    check_enum(decision, DECISIONS, "decision")
    rows, total, next_cursor = await DecisionService(db).search(
        domain=domain, decision=decision, q=q, cursor=cursor, limit=limit
    )
    return {
        "data": [DecisionRecordResponse.model_validate(x).model_dump() for x in rows],
        "meta": {"total": total, "limit": limit, "next_cursor": next_cursor},
    }


@router.get("/decisions/meta", response_model=DataResponse[dict])
async def decisions_meta(
    domain: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    check_enum(domain, EXPERIMENT_DOMAINS, "domain")
    return {"data": await DecisionService(db).meta(domain=domain)}


@router.get("/decisions/{decision_id}", response_model=DataResponse[DecisionRecordResponse])
async def get_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    return {"data": await DecisionService(db).get(decision_id)}


@router.post(
    "/decisions/{decision_id}/promotion-drafts",
    response_model=DataResponse[PromotionDraftResponse],
    status_code=201,
)
async def create_promotion_draft(
    decision_id: str,
    body: CreatePromotionDraftRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    draft = await PromotionService(db).create_draft(
        decision_id,
        target_type=body.target_type,
        target_ref=body.target_ref,
        draft_payload=body.draft_payload,
        actor=user,
    )
    await db.commit()
    return {"data": draft}


@router.get("/promotion-drafts", response_model=dict)
async def list_promotion_drafts(
    status: str | None = None,
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    check_enum(status, PROMOTION_STATUSES, "status")
    rows = await PromotionService(db).list_drafts(status=status, limit=limit)
    return {"data": [PromotionDraftResponse.model_validate(x).model_dump() for x in rows]}


@router.post(
    "/promotion-drafts/{draft_id}/approve",
    response_model=DataResponse[PromotionDraftResponse],
)
async def approve_promotion_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    draft = await PromotionService(db).approve(draft_id, actor=user)
    await db.commit()
    return {"data": draft}


@router.post(
    "/promotion-drafts/{draft_id}/reject",
    response_model=DataResponse[PromotionDraftResponse],
)
async def reject_promotion_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    draft = await PromotionService(db).reject(draft_id, actor=user)
    await db.commit()
    return {"data": draft}


@router.post(
    "/promotion-drafts/{draft_id}/apply",
    response_model=DataResponse[PromotionDraftResponse],
)
async def apply_promotion_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """Creates the target domain's DRAFT object — never a production mutation."""
    draft = await PromotionService(db).apply(draft_id, actor=user)
    await db.commit()
    return {"data": draft}


@router.post(
    "/{experiment_id}/decisions",
    response_model=DataResponse[DecisionRecordResponse],
    status_code=201,
)
async def create_decision(
    experiment_id: str,
    body: CreateDecisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    record = await DecisionService(db).create(
        experiment_id,
        decision=body.decision,
        summary=body.summary,
        analysis_result_hash=body.analysis_result_hash,
        uncertainty=body.uncertainty,
        segments=body.segments,
        evidence=body.evidence,
        extend_days=body.extend_days,
        actor=user,
    )
    await db.commit()
    return {"data": record}

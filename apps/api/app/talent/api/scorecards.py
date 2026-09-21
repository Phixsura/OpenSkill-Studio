"""Structured interview scorecard API (Phase 4D).

Authorization:
  - Templates: org member CRUD
  - Scorecards: interviewer creates/updates; org member reads
  - Submit: interviewer only; freezes the scorecard
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.application import Application, InterviewStage
from app.talent.models.employer import Opportunity
from app.talent.models.scorecard import InterviewScorecard, ScorecardTemplate
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.scorecard import (
    CreateScorecardRequest,
    CreateScorecardTemplateRequest,
    ScorecardResponse,
    ScorecardTemplateResponse,
    UpdateScorecardRequest,
    UpdateScorecardTemplateRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Scorecards"])


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


@router.post(
    "/orgs/{org_id}/scorecard-templates",
    response_model=DataResponse[ScorecardTemplateResponse],
    status_code=201,
    summary="Create Template",
)
async def create_template(
    org_id: str,
    body: CreateScorecardTemplateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a scorecard template — org member only."""
    await require_org_member(org_id, user, db)

    template = ScorecardTemplate(
        org_id=org_id,
        name=body.name,
        description=body.description,
        criteria=[c.model_dump() for c in body.criteria],
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return DataResponse(data=ScorecardTemplateResponse.model_validate(template))


@router.get(
    "/orgs/{org_id}/scorecard-templates",
    response_model=CursorListResponse[ScorecardTemplateResponse],
    summary="List Templates",
)
async def list_templates(
    org_id: str,
    status: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List scorecard templates — org member only."""
    await require_org_member(org_id, user, db)

    q = select(ScorecardTemplate).where(ScorecardTemplate.org_id == org_id)
    if status:
        q = q.where(ScorecardTemplate.status == status)
    if cursor:
        q = q.where(ScorecardTemplate.id < cursor)
    q = q.order_by(ScorecardTemplate.created_at.desc()).limit(limit + 1)

    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = items[-1].id if has_more and items else None

    return CursorListResponse(
        data=[ScorecardTemplateResponse.model_validate(t) for t in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/scorecard-templates/{template_id}",
    response_model=DataResponse[ScorecardTemplateResponse],
    summary="Get Template",
)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a scorecard template."""
    template = await db.get(ScorecardTemplate, template_id)
    if not template:
        raise HTTPException(404, "Scorecard template not found")
    await require_org_member(template.org_id, user, db)
    return DataResponse(data=ScorecardTemplateResponse.model_validate(template))


@router.patch(
    "/scorecard-templates/{template_id}",
    response_model=DataResponse[ScorecardTemplateResponse],
    summary="Update Template",
)
async def update_template(
    template_id: str,
    body: UpdateScorecardTemplateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a scorecard template — org member only."""
    template = await db.get(ScorecardTemplate, template_id)
    if not template:
        raise HTTPException(404, "Scorecard template not found")
    await require_org_member(template.org_id, user, db)

    updates = body.model_dump(exclude_unset=True)
    if "criteria" in updates and updates["criteria"] is not None:
        updates["criteria"] = [
            c.model_dump() if hasattr(c, "model_dump") else c for c in updates["criteria"]
        ]
    for key, value in updates.items():
        setattr(template, key, value)

    await db.commit()
    await db.refresh(template)
    return DataResponse(data=ScorecardTemplateResponse.model_validate(template))


# ---------------------------------------------------------------------------
# Scorecards
# ---------------------------------------------------------------------------


async def _resolve_interview_org(
    db: AsyncSession, interview_stage_id: str
) -> tuple[InterviewStage, str]:
    """Load interview stage and resolve its employer org_id."""
    stage = await db.get(InterviewStage, interview_stage_id)
    if not stage:
        raise HTTPException(404, "Interview stage not found")
    app = await db.get(Application, stage.application_id)
    if not app:
        raise HTTPException(404, "Application not found")
    opp = await db.get(Opportunity, app.opportunity_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    return stage, opp.employer_org_id


@router.post(
    "/interviews/{interview_id}/scorecards",
    response_model=DataResponse[ScorecardResponse],
    status_code=201,
    summary="Create Scorecard",
)
async def create_scorecard(
    interview_id: str,
    body: CreateScorecardRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit a scorecard for an interview — interviewer only."""
    stage, org_id = await _resolve_interview_org(db, interview_id)
    await require_org_member(org_id, user, db)

    # Check for existing scorecard by this interviewer
    existing = await db.execute(
        select(InterviewScorecard).where(
            InterviewScorecard.interview_stage_id == interview_id,
            InterviewScorecard.interviewer_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "You already submitted a scorecard for this interview")

    scorecard = InterviewScorecard(
        interview_stage_id=interview_id,
        template_id=body.template_id,
        interviewer_id=user.id,
        ratings=body.ratings,
        overall_rating=body.overall_rating,
        recommendation=body.recommendation,
        notes=body.notes,
    )
    db.add(scorecard)
    await db.commit()
    await db.refresh(scorecard)
    return DataResponse(data=ScorecardResponse.model_validate(scorecard))


@router.get(
    "/interviews/{interview_id}/scorecards",
    response_model=CursorListResponse[ScorecardResponse],
    summary="List Scorecards",
)
async def list_scorecards(
    interview_id: str,
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List scorecards for an interview — org member only."""
    _, org_id = await _resolve_interview_org(db, interview_id)
    await require_org_member(org_id, user, db)

    q = select(InterviewScorecard).where(InterviewScorecard.interview_stage_id == interview_id)
    if cursor:
        q = q.where(InterviewScorecard.id < cursor)
    q = q.order_by(InterviewScorecard.created_at.desc()).limit(limit + 1)

    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = items[-1].id if has_more and items else None

    return CursorListResponse(
        data=[ScorecardResponse.model_validate(s) for s in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.patch(
    "/scorecards/{scorecard_id}",
    response_model=DataResponse[ScorecardResponse],
    summary="Update Scorecard",
)
async def update_scorecard(
    scorecard_id: str,
    body: UpdateScorecardRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a scorecard — interviewer only, before submission."""
    scorecard = await db.get(InterviewScorecard, scorecard_id)
    if not scorecard:
        raise HTTPException(404, "Scorecard not found")
    if scorecard.interviewer_id != user.id:
        raise HTTPException(404, "Scorecard not found")
    if scorecard.submitted_at is not None:
        raise HTTPException(422, "Cannot edit a submitted scorecard")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(scorecard, key, value)

    await db.commit()
    await db.refresh(scorecard)
    return DataResponse(data=ScorecardResponse.model_validate(scorecard))


@router.post(
    "/scorecards/{scorecard_id}/submit",
    response_model=DataResponse[ScorecardResponse],
    summary="Submit Scorecard",
)
async def submit_scorecard(
    scorecard_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Finalize a scorecard — interviewer only. No further edits allowed."""
    scorecard = await db.get(InterviewScorecard, scorecard_id)
    if not scorecard:
        raise HTTPException(404, "Scorecard not found")
    if scorecard.interviewer_id != user.id:
        raise HTTPException(404, "Scorecard not found")
    if scorecard.submitted_at is not None:
        raise HTTPException(422, "Scorecard already submitted")

    scorecard.submitted_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(scorecard)
    return DataResponse(data=ScorecardResponse.model_validate(scorecard))

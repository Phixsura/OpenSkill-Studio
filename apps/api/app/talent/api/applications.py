"""Application / placement pipeline API.

Authorization rules:
  - Candidate actions (apply, withdraw, list own): app.user_id == user.id
  - Employer actions (screen, interview, offer, hire, reject): require_org_member(employer_org)
  - Interview create/update: employer org members only
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.talent.models.application import (
    APPLICATION_TRANSITIONS,
    Application,
    ApplicationEvent,
    InterviewStage,
    Placement,
)
from app.talent.models.employer import Opportunity
from app.talent.schemas.application import (
    ApplicationResponse,
    CreateApplicationRequest,
    CreateInterviewRequest,
    InterviewStageEmployerResponse,
    InterviewStageResponse,
    PlacementResponse,
    TransitionApplicationRequest,
    UpdateInterviewRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Applications"])

# Transitions that only the candidate (applicant) may perform
_CANDIDATE_TRANSITIONS = frozenset({"withdrawn"})
# Transitions that only the employer may perform
_EMPLOYER_TRANSITIONS = frozenset(
    {"screening", "interview", "assessment", "offer", "rejected", "hired", "completed"}
)
# Transitions allowed from either side
_EITHER_TRANSITIONS = frozenset({"submitted"})


async def _load_app_and_opp(
    db: AsyncSession, app_id: str
) -> tuple[Application, Opportunity]:
    """Load application + its opportunity, or raise 404."""
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    opp = await db.get(Opportunity, app.opportunity_id)
    if not opp:
        raise HTTPException(404, "Application not found")
    return app, opp


@router.post(
    "/opportunities/{opp_id}/apply",
    response_model=DataResponse[ApplicationResponse],
    status_code=201,
)
async def apply_to_opportunity(
    opp_id: str,
    body: CreateApplicationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit an application to an opportunity."""
    opp = await db.get(Opportunity, opp_id)
    if not opp or opp.status != "open":
        raise HTTPException(404, "Opportunity not found or not open")

    # Check for existing application
    existing = await db.execute(
        select(Application).where(
            Application.user_id == user.id,
            Application.opportunity_id == opp_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "You have already applied to this opportunity")

    # Build evidence bundle (frozen at submission time)
    evidence_bundle = {
        "snapshot_at": datetime.now(UTC).isoformat(),
        "selected_credentials": body.selected_credentials,
        "selected_projects": body.selected_projects,
        "selected_evidence": body.selected_evidence,
    }

    app = Application(
        opportunity_id=opp_id,
        user_id=user.id,
        evidence_bundle=evidence_bundle,
        status="submitted",
        cover_note=body.cover_note,
        resume_asset_id=body.resume_asset_id,
    )
    db.add(app)
    await db.flush()

    # Audit event
    event = ApplicationEvent(
        application_id=app.id,
        from_status="draft",
        to_status="submitted",
        acted_by=user.id,
    )
    db.add(event)
    await db.commit()

    # Webhook: application.submitted
    from app.talent.services.webhook_events import emit_talent_event

    await emit_talent_event(
        db,
        org_id=opp.employer_org_id,
        event_type="application.submitted",
        payload={
            "application_id": app.id,
            "opportunity_id": opp_id,
            "user_id": user.id,
        },
    )

    return DataResponse(data=ApplicationResponse.model_validate(app))


@router.get("/applications", response_model=ListResponse[ApplicationResponse])
async def list_applications(
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List own applications (candidate view)."""
    q = select(Application).where(Application.user_id == user.id)
    if status:
        q = q.where(Application.status == status)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(Application.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
    result = await db.execute(q)
    items = result.scalars().all()

    return ListResponse(
        data=[ApplicationResponse.model_validate(a) for a in items],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=page * per_page < total),
    )


@router.get("/applications/{app_id}", response_model=DataResponse[ApplicationResponse])
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app, opp = await _load_app_and_opp(db, app_id)

    # Candidate sees own application
    if app.user_id == user.id:
        return DataResponse(data=ApplicationResponse.model_validate(app))

    # Employer org members can see applications to their opportunities
    await require_org_member(opp.employer_org_id, user, db)
    return DataResponse(data=ApplicationResponse.model_validate(app))


@router.patch(
    "/applications/{app_id}/status",
    response_model=DataResponse[ApplicationResponse],
)
async def transition_application(
    app_id: str,
    body: TransitionApplicationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Transition an application status.

    Authorization:
      - Candidate may only withdraw their own application.
      - Employer org members may perform employer-side transitions.
    """
    app, opp = await _load_app_and_opp(db, app_id)

    # Validate transition is allowed by state machine
    allowed = APPLICATION_TRANSITIONS.get(app.status, [])
    if body.status not in allowed:
        raise HTTPException(
            422,
            f"Cannot transition from '{app.status}' to '{body.status}'. "
            f"Allowed: {allowed}",
        )

    # Authorization: who may perform this transition?
    if body.status in _CANDIDATE_TRANSITIONS:
        # Only the applicant can withdraw
        if app.user_id != user.id:
            raise HTTPException(404, "Application not found")
    elif body.status in _EMPLOYER_TRANSITIONS:
        # Only employer org members can screen/interview/offer/hire/reject
        await require_org_member(opp.employer_org_id, user, db)
    elif body.status in _EITHER_TRANSITIONS:
        # submitted: must be the applicant
        if app.user_id != user.id:
            raise HTTPException(404, "Application not found")
    else:
        raise HTTPException(403, "Unauthorized transition")

    old_status = app.status
    app.status = body.status

    # Audit event — acted_by is ALWAYS required (structural enforcement)
    event = ApplicationEvent(
        application_id=app.id,
        from_status=old_status,
        to_status=body.status,
        acted_by=user.id,  # NOT nullable
        note=body.note,
    )
    db.add(event)

    # Auto-create placement on hire
    if body.status == "hired":
        placement = Placement(
            application_id=app.id,
            opportunity_id=app.opportunity_id,
            user_id=app.user_id,
            employer_org_id=opp.employer_org_id,
            placement_source="platform_match" if app.match_run_id else "direct_apply",
        )
        db.add(placement)

    await db.commit()

    # Webhook events for application transitions
    from app.talent.services.webhook_events import emit_talent_event

    event_type = "application.stage_changed"
    if body.status == "offer":
        event_type = "offer.created"
    elif body.status == "hired":
        event_type = "placement.started"

    await emit_talent_event(
        db,
        org_id=opp.employer_org_id,
        event_type=event_type,
        payload={
            "application_id": app.id,
            "opportunity_id": app.opportunity_id,
            "user_id": app.user_id,
            "from_status": old_status,
            "to_status": body.status,
        },
    )

    return DataResponse(data=ApplicationResponse.model_validate(app))


# ---- Interviews ----

@router.post(
    "/applications/{app_id}/interviews",
    response_model=DataResponse[InterviewStageResponse],
    status_code=201,
)
async def create_interview(
    app_id: str,
    body: CreateInterviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create an interview stage — employer org members only."""
    app, opp = await _load_app_and_opp(db, app_id)
    await require_org_member(opp.employer_org_id, user, db)

    stage = InterviewStage(
        application_id=app_id,
        stage_type=body.stage_type,
        interviewer_id=body.interviewer_id,
        scheduled_at=body.scheduled_at,
    )
    db.add(stage)
    await db.commit()
    return DataResponse(data=InterviewStageResponse.model_validate(stage))


@router.patch(
    "/applications/{app_id}/interviews/{interview_id}",
    response_model=DataResponse[InterviewStageEmployerResponse],
)
async def update_interview(
    app_id: str,
    interview_id: str,
    body: UpdateInterviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update an interview stage — employer org members only."""
    app, opp = await _load_app_and_opp(db, app_id)
    await require_org_member(opp.employer_org_id, user, db)

    stage = await db.get(InterviewStage, interview_id)
    if not stage or stage.application_id != app_id:
        raise HTTPException(404, "Interview stage not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(stage, key, value)

    await db.commit()
    return DataResponse(data=InterviewStageEmployerResponse.model_validate(stage))


# ---- Placements ----

@router.get("/placements", response_model=ListResponse[PlacementResponse])
async def list_placements(
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List placements for the current user."""
    q = select(Placement).where(Placement.user_id == user.id)
    if status:
        q = q.where(Placement.status == status)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(Placement.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
    result = await db.execute(q)
    items = result.scalars().all()

    return ListResponse(
        data=[PlacementResponse.model_validate(p) for p in items],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=page * per_page < total),
    )

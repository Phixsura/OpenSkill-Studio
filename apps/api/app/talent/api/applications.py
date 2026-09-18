"""Application / placement pipeline API.

Authorization rules:
  - Candidate actions (apply, withdraw, list own): app.user_id == user.id
  - Employer actions (screen, interview, offer, hire, reject): require_org_member(employer_org)
  - Interview create/update: employer org members only
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
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
    CreateFeedbackRequest,
    CreateInterviewRequest,
    FeedbackResponse,
    InterviewStageEmployerResponse,
    InterviewStageResponse,
    PlacementResponse,
    TransitionApplicationRequest,
    UpdateFeedbackVisibilityRequest,
    UpdateInterviewRequest,
)
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Applications"])

# Transitions that only the candidate (applicant) may perform
_CANDIDATE_TRANSITIONS = frozenset({"withdrawn", "accepted"})
# Transitions that only the employer may perform
_EMPLOYER_TRANSITIONS = frozenset(
    {"screening", "interview", "assessment", "offer", "rejected", "hired", "completed"}
)
# Transitions allowed from either side
_EITHER_TRANSITIONS = frozenset({"submitted"})


async def _load_app_and_opp(db: AsyncSession, app_id: str) -> tuple[Application, Opportunity]:
    """Load application + its opportunity, or raise 404."""
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    opp = await db.get(Opportunity, app.opportunity_id)
    if not opp:
        raise HTTPException(404, "Application not found")
    return app, opp


@router.post(
    "/applications",
    response_model=DataResponse[ApplicationResponse],
    status_code=201,
    summary="Create application",
    description="Submit an application to an opportunity. Frontend-friendly alias that accepts opportunity_id in the body.",
)
async def create_application(
    body: CreateApplicationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create application — accepts {opportunity_id} in body."""
    opp_id = body.opportunity_id
    opp = await db.get(Opportunity, opp_id)
    if not opp or opp.status != "open":
        raise HTTPException(404, "Opportunity not found or not open")
    existing = await db.execute(
        select(Application).where(
            Application.user_id == user.id,
            Application.opportunity_id == opp_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "You have already applied to this opportunity")
    from ulid import ULID

    app = Application(
        id=str(ULID()),
        user_id=user.id,
        opportunity_id=opp_id,
        status="submitted",
        evidence_bundle=body.evidence_bundle if hasattr(body, "evidence_bundle") else None,
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return DataResponse(data=ApplicationResponse.model_validate(app))


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

    await db.refresh(app)
    return DataResponse(data=ApplicationResponse.model_validate(app))


@router.get(
    "/applications/analytics",
    response_model=DataResponse[dict],
    summary="Get application analytics",
    description="Aggregated analytics including conversion rates and status breakdown.",
)
async def get_application_analytics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Candidate-side application analytics — success rate, response time, etc."""
    import dataclasses

    from app.talent.services.candidate_analytics import CandidateAnalyticsService

    svc = CandidateAnalyticsService(db)
    stats = await svc.get_stats(user.id)
    return DataResponse(data=dataclasses.asdict(stats))


@router.get(
    "/applications",
    response_model=CursorListResponse[ApplicationResponse],
    summary="List applications",
    description="Paginated list of user job applications with status.",
)
async def list_applications(
    status: str | None = None,
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List own applications (candidate view)."""
    q = select(Application).where(Application.user_id == user.id)
    if status:
        q = q.where(Application.status == status)

    if cursor:
        q = q.where(Application.id < cursor)
    q = q.order_by(Application.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = result.scalars().all()

    all_items = list(items) if not isinstance(items, list) else items
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[ApplicationResponse.model_validate(a) for a in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.get(
    "/applications/{app_id}",
    response_model=DataResponse[ApplicationResponse],
    summary="Get application detail",
    description="Full application details including evidence bundle and messages.",
)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app, opp = await _load_app_and_opp(db, app_id)

    # Candidate sees own application
    if app.user_id == user.id:
        await db.refresh(app)
        return DataResponse(data=ApplicationResponse.model_validate(app))

    # Employer org members can see applications to their opportunities
    await require_org_member(opp.employer_org_id, user, db)
    await db.refresh(app)
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
            f"Cannot transition from '{app.status}' to '{body.status}'. Allowed: {allowed}",
        )

    # Authorization: who may perform this transition?
    if body.status in _CANDIDATE_TRANSITIONS:
        # Only the applicant can withdraw
        if app.user_id != user.id:
            raise HTTPException(404, "Application not found")
    elif body.status in _EMPLOYER_TRANSITIONS:
        # Only employer org members can screen/interview/offer/hire/reject.
        # TODO: tighten to HIRING_MANAGER+ once employer role assignment
        # UI is in place (OrgRole.HIRING_MANAGER, OrgRole.ADMIN, OrgRole.OWNER).
        # Currently any org member can perform these transitions.
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

    # Notify the applicant about the status change
    from app.talent.services.notifications import TalentNotificationService

    notif_svc = TalentNotificationService(db)
    status_messages = {
        "screening": "Your application is being reviewed",
        "interview": "You've been selected for an interview!",
        "assessment": "You have an assessment to complete",
        "offer": "Congratulations! You've received an offer!",
        "rejected": "Your application was not selected this time",
        "hired": "Welcome aboard! Your placement has been confirmed",
    }
    notif_message = status_messages.get(
        body.status, f"Your application status changed to {body.status}"
    )
    try:
        await notif_svc.send(
            user_id=app.user_id,
            event_type="application_status_changed",
            title=f"Application Update: {opp.title}",
            message=notif_message,
            metadata={
                "application_id": app.id,
                "opportunity_id": app.opportunity_id,
                "from_status": old_status,
                "to_status": body.status,
            },
        )
        await db.commit()
    except Exception:
        pass  # Notification failure must not block transition

    await db.refresh(app)
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
    await db.refresh(stage)
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
    await db.refresh(stage)
    return DataResponse(data=InterviewStageEmployerResponse.model_validate(stage))


# ---- Placements ----


@router.get(
    "/placements",
    response_model=CursorListResponse[PlacementResponse],
    summary="List placements",
    description="Paginated list of confirmed placements.",
)
async def list_placements(
    status: str | None = None,
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List placements for the current user."""
    q = select(Placement).where(Placement.user_id == user.id)
    if status:
        q = q.where(Placement.status == status)

    if cursor:
        q = q.where(Placement.id < cursor)
    q = q.order_by(Placement.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = result.scalars().all()

    all_items = list(items) if not isinstance(items, list) else items
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[PlacementResponse.model_validate(p) for p in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


# ---- Feedback ----


@router.post(
    "/applications/{app_id}/feedback",
    response_model=DataResponse[FeedbackResponse],
    status_code=201,
)
async def add_feedback(
    app_id: str,
    body: CreateFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Add feedback to an application — employer org members only."""
    app, opp = await _load_app_and_opp(db, app_id)
    await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.application_feedback import ApplicationFeedbackService

    svc = ApplicationFeedbackService(db)
    try:
        feedback = await svc.add_feedback(
            application_id=app_id,
            feedback_type=body.feedback_type,
            content=body.content,
            visibility=body.visibility,
            author_id=user.id,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    await db.commit()
    await db.refresh(feedback)
    return DataResponse(data=FeedbackResponse.model_validate(feedback))


@router.get(
    "/applications/{app_id}/feedback",
    response_model=DataResponse[list[FeedbackResponse]],
)
async def list_feedback(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List feedback for an application.

    Employer org members see all feedback.
    Candidates see only 'shared_with_candidate' feedback.
    """
    app, opp = await _load_app_and_opp(db, app_id)

    is_employer = False
    if app.user_id != user.id:
        # Not the candidate — must be employer org member
        await require_org_member(opp.employer_org_id, user, db)
        is_employer = True

    from app.talent.services.application_feedback import ApplicationFeedbackService

    svc = ApplicationFeedbackService(db)
    items = await svc.list_feedback(app_id, viewer_user_id=user.id, is_employer=is_employer)
    return DataResponse(data=[FeedbackResponse.model_validate(f) for f in items])


@router.patch(
    "/feedback/{feedback_id}/visibility",
    response_model=DataResponse[FeedbackResponse],
)
async def update_feedback_visibility(
    feedback_id: str,
    body: UpdateFeedbackVisibilityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Change feedback visibility — author only."""
    from app.talent.services.application_feedback import ApplicationFeedbackService

    svc = ApplicationFeedbackService(db)
    try:
        feedback = await svc.update_visibility(feedback_id, body.visibility, user.id)
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    if not feedback:
        raise HTTPException(404, "Feedback not found or not the author")

    await db.commit()
    await db.refresh(feedback)
    return DataResponse(data=FeedbackResponse.model_validate(feedback))


# ---- Application Comparison (N16) ----


class CompareRequest(BaseModel):
    application_ids: list[str] = Field(..., min_length=2, max_length=10)


@router.post(
    "/opportunities/{opp_id}/compare",
    response_model=DataResponse[list[dict]],
)
async def compare_applications(
    opp_id: str,
    body: CompareRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Compare candidates side-by-side — employer org members only."""
    opp = await db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.application_comparison import (
        ApplicationComparisonService,
    )

    svc = ApplicationComparisonService(db)
    try:
        comparisons = await svc.compare(opp_id, body.application_ids)
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    import dataclasses

    return DataResponse(data=[dataclasses.asdict(c) for c in comparisons])


# ---- Gap #81: Custom questions validation ----


@router.post(
    "/opportunities/{opp_id}/custom-questions/validate",
    response_model=DataResponse[dict],
    summary="Validate custom questions",
    description="Validate answers to custom application questions.",
)
async def validate_custom_questions_endpoint(
    opp_id: str,
    body: dict,
    user: User = Depends(get_current_user),
):
    """Validate custom application questions for an opportunity."""
    from app.talent.services.application_intelligence import validate_custom_questions

    errors = validate_custom_questions(body.get("questions", []))
    return DataResponse(data={"valid": len(errors) == 0, "errors": errors})


# ---- Gap #82: Auto-screening ----


@router.post(
    "/applications/{app_id}/screen",
    response_model=DataResponse[dict],
    summary="Screen application",
    description="Run automated screening against opportunity requirements.",
)
async def auto_screen_application(
    app_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Run auto-screening rules against a candidate's data."""
    from app.talent.services.application_intelligence import evaluate_screening_rules

    result = evaluate_screening_rules(body.get("rules", []), body.get("candidate_data", {}))
    return DataResponse(data=result)


# ---- Gap #86: Application timeline ----


@router.get(
    "/applications/{app_id}/timeline",
    response_model=DataResponse[list[dict]],
    summary="Get application timeline",
    description="Full timeline of status changes for an application.",
)
async def get_application_timeline(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get detailed application timeline with stage durations."""
    import dataclasses

    from app.talent.services.application_intelligence import build_application_timeline

    app = await db.get(Application, app_id)
    if not app or app.user_id != user.id:
        opp = await db.get(Opportunity, app.opportunity_id) if app else None
        if opp:
            await require_org_member(opp.employer_org_id, user, db)
        else:
            raise HTTPException(404, "Application not found")
    # Load events
    from sqlalchemy import select as sa_select

    result = await db.execute(
        sa_select(ApplicationEvent)
        .where(ApplicationEvent.application_id == app_id)
        .order_by(ApplicationEvent.created_at)
    )
    events = [
        {
            "to_status": e.to_status,
            "timestamp": e.created_at.isoformat() if e.created_at else None,
            "acted_by": e.acted_by,
            "note": e.note,
        }
        for e in result.scalars().all()
    ]
    timeline = build_application_timeline(events)
    return DataResponse(data=[dataclasses.asdict(t) for t in timeline])


# ---- Gap #92: Stage overdue check ----


@router.get(
    "/applications/{app_id}/overdue",
    response_model=DataResponse[dict],
    summary="Check application overdue",
    description="Check if application exceeded expected response time.",
)
async def check_application_overdue(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check if application has exceeded stage time limit."""
    from app.talent.services.application_intelligence import check_stage_overdue

    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    if app.user_id != user.id:
        opp = await db.get(Opportunity, app.opportunity_id)
        if not opp:
            raise HTTPException(404, "Application not found")
        await require_org_member(opp.employer_org_id, user, db)
    result = check_stage_overdue(app.status, app.updated_at or app.created_at)
    return DataResponse(data=result)

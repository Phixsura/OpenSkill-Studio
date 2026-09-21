"""Employer verification + internship supervision API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.application import Placement
from app.talent.models.internship import (
    CohortOpportunityExposure,
    InternshipSupervision,
)
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.verification import (
    CohortExposureResponse,
    CreateSupervisionRequest,
    CreateVerificationRequest,
    ExposeOpportunityRequest,
    SupervisionResponse,
    UpdateSupervisionRequest,
    VerificationResponse,
)

router = APIRouter(prefix="/talent", tags=["Talent — Verifications"])

_INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Employer Verification ──


@router.post(
    "/placements/{placement_id}/verification",
    response_model=DataResponse[VerificationResponse],
    status_code=201,
    summary="Create Verification",
)
async def create_verification(
    placement_id: str,
    body: CreateVerificationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit employer verification after a placement — employer org members only."""
    placement = await db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(404, "Placement not found")
    await require_org_member(placement.employer_org_id, user, db)

    from app.talent.services.employer_verification import EmployerVerificationService

    svc = EmployerVerificationService(db)
    try:
        verification = await svc.create_verification(
            placement_id=placement_id,
            employer_org_id=placement.employer_org_id,
            verified_by=user.id,
            user_id=placement.user_id,
            capability_ratings=body.capability_ratings,
            overall_rating=body.overall_rating,
            overall_comment=body.overall_comment,
        )
    except ValueError as e:
        raise HTTPException(422, "Validation error") from e
    await db.commit()

    # Webhook: employer_verification.submitted + capability.verified
    from app.talent.services.webhook_events import emit_talent_event

    await emit_talent_event(
        db,
        org_id=placement.employer_org_id,
        event_type="employer_verification.submitted",
        payload={
            "verification_id": verification.id,
            "placement_id": placement_id,
            "user_id": placement.user_id,
        },
    )
    for rating in body.capability_ratings:
        await emit_talent_event(
            db,
            org_id=placement.employer_org_id,
            event_type="capability.verified",
            payload={
                "user_id": placement.user_id,
                "capability_id": rating.get("capability_id"),
                "verification_id": verification.id,
                "verification_level": "employer_verified",
            },
        )

    return DataResponse(data=VerificationResponse.model_validate(verification))


# ── Internship Supervision ──


@router.post(
    "/supervisions",
    response_model=DataResponse[SupervisionResponse],
    status_code=201,
    summary="Create Supervision",
)
async def create_supervision(
    body: CreateSupervisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create internship supervision record — school instructor+ only."""
    await require_org_member(body.school_org_id, user, db, *_INSTRUCTOR_ROLES)

    # Validate placement exists
    placement = await db.get(Placement, body.placement_id)
    if not placement:
        raise HTTPException(404, "Placement not found")

    # Validate the placed student is enrolled in a cohort of this school
    from app.models.cohort import Cohort, CohortMember

    linked = await db.execute(
        select(CohortMember.id)
        .join(Cohort, Cohort.id == CohortMember.cohort_id)
        .where(
            CohortMember.user_id == placement.user_id,
            Cohort.org_id == body.school_org_id,
        )
        .limit(1)
    )
    if linked.scalar_one_or_none() is None:
        raise HTTPException(404, "Placement not found")

    supervision = InternshipSupervision(
        placement_id=body.placement_id,
        school_org_id=body.school_org_id,
        supervisor_user_id=body.supervisor_user_id,
        employer_mentor_name=body.employer_mentor_name,
    )
    db.add(supervision)
    await db.commit()
    await db.refresh(supervision)
    return DataResponse(data=SupervisionResponse.model_validate(supervision))


@router.get(
    "/supervisions",
    response_model=CursorListResponse[SupervisionResponse],
    summary="List Supervisions",
)
async def list_supervisions(
    school_org_id: str = Query(...),
    status: str | None = None,
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(school_org_id, user, db)

    q = select(InternshipSupervision).where(InternshipSupervision.school_org_id == school_org_id)
    if status:
        q = q.where(InternshipSupervision.status == status)

    if cursor:
        q = q.where(InternshipSupervision.id < cursor)
    q = q.order_by(InternshipSupervision.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    all_items = list(result.scalars().all())
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[SupervisionResponse.model_validate(s) for s in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.patch(
    "/supervisions/{supervision_id}",
    response_model=DataResponse[SupervisionResponse],
    summary="Update Supervision",
)
async def update_supervision(
    supervision_id: str,
    body: UpdateSupervisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sup = await db.get(InternshipSupervision, supervision_id)
    if not sup:
        raise HTTPException(404, "Supervision not found")
    await require_org_member(sup.school_org_id, user, db, *_INSTRUCTOR_ROLES)

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(sup, key, value)

    await db.commit()
    await db.refresh(sup)
    return DataResponse(data=SupervisionResponse.model_validate(sup))


# ── Cohort Exposure ──


@router.post(
    "/cohorts/{cohort_id}/expose",
    response_model=DataResponse[CohortExposureResponse],
    status_code=201,
    summary="Expose Opportunity",
)
async def expose_opportunity(
    cohort_id: str,
    body: ExposeOpportunityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Expose an opportunity to a cohort — instructor+ only.

    This does NOT share student data — students must individually opt in.
    """
    from app.models.cohort import Cohort

    cohort = await db.get(Cohort, cohort_id)
    if not cohort:
        raise HTTPException(404, "Cohort not found")
    await require_org_member(cohort.org_id, user, db, *_INSTRUCTOR_ROLES)

    exposure = CohortOpportunityExposure(
        cohort_id=cohort_id,
        opportunity_id=body.opportunity_id,
        exposed_by=user.id,
        note=body.note,
    )
    db.add(exposure)
    await db.commit()
    await db.refresh(exposure)
    return DataResponse(data=CohortExposureResponse.model_validate(exposure))


@router.get(
    "/cohorts/{cohort_id}/opportunities",
    response_model=DataResponse[list[CohortExposureResponse]],
    summary="List Cohort Opportunities",
)
async def list_cohort_opportunities(
    cohort_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models.cohort import Cohort

    cohort = await db.get(Cohort, cohort_id)
    if not cohort:
        raise HTTPException(404, "Cohort not found")
    await require_org_member(cohort.org_id, user, db)

    result = await db.execute(
        select(CohortOpportunityExposure)
        .where(CohortOpportunityExposure.cohort_id == cohort_id)
        .order_by(CohortOpportunityExposure.created_at.desc())
    )
    return DataResponse(
        data=[CohortExposureResponse.model_validate(e) for e in result.scalars().all()]
    )

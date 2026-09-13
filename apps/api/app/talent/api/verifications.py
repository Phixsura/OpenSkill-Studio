"""Employer verification + internship supervision API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.talent.models.application import Placement
from app.talent.models.internship import (
    CohortOpportunityExposure,
    InternshipSupervision,
)

router = APIRouter(prefix="/talent", tags=["Talent — Verifications"])

_INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Employer Verification ──

@router.post(
    "/placements/{placement_id}/verification",
    response_model=DataResponse[dict],
    status_code=201,
)
async def create_verification(
    placement_id: str,
    body: dict,  # capability_ratings, overall_rating, overall_comment
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
            capability_ratings=body.get("capability_ratings", []),
            overall_rating=body.get("overall_rating"),
            overall_comment=body.get("overall_comment"),
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    return DataResponse(data={
        "id": verification.id,
        "placement_id": verification.placement_id,
        "user_id": verification.user_id,
        "capability_ratings": verification.capability_ratings,
        "overall_rating": float(verification.overall_rating) if verification.overall_rating else None,
        "created_at": verification.created_at.isoformat() if verification.created_at else None,
    })


# ── Internship Supervision ──

@router.post("/supervisions", response_model=DataResponse[dict], status_code=201)
async def create_supervision(
    body: dict,  # placement_id, school_org_id, supervisor_user_id, employer_mentor_name
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create internship supervision record — school instructor+ only."""
    school_org_id = body.get("school_org_id")
    if not school_org_id:
        raise HTTPException(422, "school_org_id is required")
    await require_org_member(school_org_id, user, db, *_INSTRUCTOR_ROLES)

    placement_id = body.get("placement_id")
    if not placement_id:
        raise HTTPException(422, "placement_id is required")

    # Validate placement exists
    placement = await db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(404, "Placement not found")

    # Validate the placed student is enrolled in a cohort of this school
    from app.models.cohort import Cohort, CohortMember

    linked = await db.execute(
        select(CohortMember.id)
        .join(Cohort, Cohort.id == CohortMember.cohort_id)
        .where(
            CohortMember.user_id == placement.user_id,
            Cohort.org_id == school_org_id,
        )
        .limit(1)
    )
    if linked.scalar_one_or_none() is None:
        raise HTTPException(403, "Placement is not associated with this school")

    supervision = InternshipSupervision(
        placement_id=placement_id,
        school_org_id=school_org_id,
        supervisor_user_id=body.get("supervisor_user_id"),
        employer_mentor_name=body.get("employer_mentor_name"),
    )
    db.add(supervision)
    await db.commit()
    return DataResponse(data={
        "id": supervision.id,
        "placement_id": supervision.placement_id,
        "school_org_id": supervision.school_org_id,
        "status": supervision.status,
    })


@router.get("/supervisions", response_model=ListResponse[dict])
async def list_supervisions(
    school_org_id: str = Query(...),
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(school_org_id, user, db)

    q = select(InternshipSupervision).where(InternshipSupervision.school_org_id == school_org_id)
    if status:
        q = q.where(InternshipSupervision.status == status)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(InternshipSupervision.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
    result = await db.execute(q)
    items = [
        {
            "id": s.id,
            "placement_id": s.placement_id,
            "school_org_id": s.school_org_id,
            "supervisor_user_id": s.supervisor_user_id,
            "status": s.status,
        }
        for s in result.scalars().all()
    ]
    return ListResponse(
        data=items,
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=page * per_page < total),
    )


@router.patch("/supervisions/{supervision_id}", response_model=DataResponse[dict])
async def update_supervision(
    supervision_id: str,
    body: dict,  # milestones, notes, status
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sup = await db.get(InternshipSupervision, supervision_id)
    if not sup:
        raise HTTPException(404, "Supervision not found")
    await require_org_member(sup.school_org_id, user, db, *_INSTRUCTOR_ROLES)

    for key in ("milestones", "notes", "status", "supervisor_user_id", "employer_mentor_name"):
        if key in body:
            setattr(sup, key, body[key])

    await db.commit()
    return DataResponse(data={
        "id": sup.id,
        "placement_id": sup.placement_id,
        "status": sup.status,
        "milestones": sup.milestones,
    })


# ── Cohort Exposure ──

@router.post("/cohorts/{cohort_id}/expose", response_model=DataResponse[dict], status_code=201)
async def expose_opportunity(
    cohort_id: str,
    body: dict,  # opportunity_id, note
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Expose an opportunity to a cohort — instructor+ only.

    This does NOT share student data — students must individually opt in.
    """
    # Need to find the cohort's org to check membership
    from app.models.cohort import Cohort

    cohort = await db.get(Cohort, cohort_id)
    if not cohort:
        raise HTTPException(404, "Cohort not found")
    await require_org_member(cohort.org_id, user, db, *_INSTRUCTOR_ROLES)

    opportunity_id = body.get("opportunity_id")
    if not opportunity_id:
        raise HTTPException(422, "opportunity_id is required")

    exposure = CohortOpportunityExposure(
        cohort_id=cohort_id,
        opportunity_id=opportunity_id,
        exposed_by=user.id,
        note=body.get("note"),
    )
    db.add(exposure)
    await db.commit()
    return DataResponse(data={
        "id": exposure.id,
        "cohort_id": exposure.cohort_id,
        "opportunity_id": exposure.opportunity_id,
    })


@router.get("/cohorts/{cohort_id}/opportunities", response_model=DataResponse[list[dict]])
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
    items = [
        {
            "id": e.id,
            "cohort_id": e.cohort_id,
            "opportunity_id": e.opportunity_id,
            "exposed_by": e.exposed_by,
            "note": e.note,
        }
        for e in result.scalars().all()
    ]
    return DataResponse(data=items)

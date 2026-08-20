"""Cohort management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.cohort import CohortRole
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.cohort import (
    AddCohortMemberRequest,
    AssignProjectRequest,
    AssignSkillRequest,
    BulkEnrollRequest,
    CohortMemberResponse,
    CohortProjectAssignmentResponse,
    CohortResponse,
    CohortSkillAssignmentResponse,
    CreateCohortRequest,
    UpdateCohortRequest,
)
from app.services.cohort import CohortService

router = APIRouter(tags=["Cohorts"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


def _cohort_response(cohort, member_count: int = 0) -> CohortResponse:
    resp = CohortResponse.model_validate(cohort)
    resp.member_count = member_count
    return resp


# ── CRUD ──────────────────────────────────────────────────


@router.post("/orgs/{org_id}/cohorts", response_model=DataResponse[CohortResponse], status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def create_cohort(
    org_id: str,
    body: CreateCohortRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    cohort = await svc.create_cohort(
        org_id,
        body.name,
        body.description,
        body.starts_at,
        body.ends_at,
        body.max_learners,
        user.id,
    )
    await db.commit()
    return DataResponse(data=_cohort_response(cohort))


@router.get("/orgs/{org_id}/cohorts", response_model=ListResponse[CohortResponse], dependencies=[Depends(rate_limit(20, 60))])
async def list_cohorts(
    org_id: str,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = CohortService(db)
    cohorts, total = await svc.list_cohorts(org_id, status, page, per_page)
    items = []
    for c in cohorts:
        count = await svc.get_member_count(c.id)
        items.append(_cohort_response(c, count))
    return ListResponse(
        data=items,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get("/orgs/{org_id}/cohorts/{cohort_id}", response_model=DataResponse[CohortResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_cohort(
    org_id: str,
    cohort_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = CohortService(db)
    cohort = await svc.get_cohort(cohort_id)
    if cohort.org_id != org_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    count = await svc.get_member_count(cohort_id)
    return DataResponse(data=_cohort_response(cohort, count))


@router.put("/orgs/{org_id}/cohorts/{cohort_id}", response_model=DataResponse[CohortResponse], dependencies=[Depends(rate_limit(20, 60))])
async def update_cohort(
    org_id: str,
    cohort_id: str,
    body: UpdateCohortRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    cohort = await svc.get_cohort(cohort_id)
    if cohort.org_id != org_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    cohort = await svc.update_cohort(cohort_id, **body.model_dump(exclude_none=True))
    await db.commit()
    count = await svc.get_member_count(cohort_id)
    return DataResponse(data=_cohort_response(cohort, count))


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def delete_cohort(
    org_id: str,
    cohort_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    cohort = await svc.get_cohort(cohort_id)
    if cohort.org_id != org_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    await svc.delete_cohort(cohort_id)
    await db.commit()


# ── Members ───────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/cohorts/{cohort_id}/members",
    response_model=DataResponse[CohortMemberResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def add_member(
    org_id: str,
    cohort_id: str,
    body: AddCohortMemberRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    member = await svc.add_member(cohort_id, body.user_id, CohortRole(body.role), org_id)
    await db.commit()
    return DataResponse(data=CohortMemberResponse.model_validate(member))


@router.post(
    "/orgs/{org_id}/cohorts/{cohort_id}/members/bulk",
    response_model=DataResponse[dict],
    status_code=200,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def bulk_enroll(
    org_id: str,
    cohort_id: str,
    body: BulkEnrollRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    enrolled = 0
    skipped = 0
    errors: list[str] = []
    role = CohortRole(body.role)
    for uid in body.user_ids:
        try:
            await svc.add_member(cohort_id, uid, role, org_id)
            enrolled += 1
        except AppError as e:
            skipped += 1
            if e.code == "COHORT_FULL":
                errors.append(f"Cohort is full (max {e.message})")
                break  # No point trying more
            # ALREADY_MEMBER, USER_NOT_FOUND, COHORT_FROZEN — continue
        except Exception:  # noqa: BLE001 — unexpected errors
            skipped += 1
    await db.commit()
    result: dict = {"enrolled": enrolled, "skipped": skipped}
    if errors:
        result["errors"] = errors
    return DataResponse(data=result)


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}/members/{user_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def remove_member(
    org_id: str,
    cohort_id: str,
    user_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    await svc.remove_member(cohort_id, user_id, org_id)
    await db.commit()


@router.get(
    "/orgs/{org_id}/cohorts/{cohort_id}/members",
    response_model=ListResponse[CohortMemberResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_members(
    org_id: str,
    cohort_id: str,
    role: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    cohort = await svc.get_cohort(cohort_id)
    if cohort.org_id != org_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    members, total = await svc.list_members(cohort_id, role, page, per_page)
    items = [
        CohortMemberResponse(
            **CohortMemberResponse.model_validate(m).model_dump()
            | {"user_name": name, "user_email": email}
        )
        for m, name, email in members
    ]
    return ListResponse(
        data=items,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


# ── Skill Assignment ─────────────────────────────────────


@router.post(
    "/orgs/{org_id}/cohorts/{cohort_id}/skills",
    response_model=DataResponse[CohortSkillAssignmentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def assign_skill(
    org_id: str,
    cohort_id: str,
    body: AssignSkillRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    assignment = await svc.assign_skill(cohort_id, body.skill_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=CohortSkillAssignmentResponse.model_validate(assignment))


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}/skills/{skill_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def unassign_skill(
    org_id: str,
    cohort_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    await svc.unassign_skill(cohort_id, skill_id, org_id)
    await db.commit()


@router.get(
    "/orgs/{org_id}/cohorts/{cohort_id}/skills",
    response_model=DataResponse[list[CohortSkillAssignmentResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_assigned_skills(
    org_id: str,
    cohort_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = CohortService(db)
    cohort = await svc.get_cohort(cohort_id)
    if cohort.org_id != org_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    assignments = await svc.list_assigned_skills(cohort_id)
    return DataResponse(
        data=[
            CohortSkillAssignmentResponse(
                **CohortSkillAssignmentResponse.model_validate(a).model_dump()
                | {"skill_name": name}
            )
            for a, name in assignments
        ]
    )


# ── Project Assignment ───────────────────────────────────


@router.post(
    "/orgs/{org_id}/cohorts/{cohort_id}/projects",
    response_model=DataResponse[CohortProjectAssignmentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def assign_project(
    org_id: str,
    cohort_id: str,
    body: AssignProjectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    assignment = await svc.assign_project(
        cohort_id,
        body.project_id,
        org_id,
        user.id,
        body.deadline_override,
        body.late_deadline_override,
        body.max_submissions_override,
        body.participation_mode,
    )
    await db.commit()
    return DataResponse(data=CohortProjectAssignmentResponse.model_validate(assignment))


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}/projects/{project_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def unassign_project(
    org_id: str,
    cohort_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    await svc.unassign_project(cohort_id, project_id, org_id)
    await db.commit()


@router.get(
    "/orgs/{org_id}/cohorts/{cohort_id}/projects",
    response_model=DataResponse[list[CohortProjectAssignmentResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_assigned_projects(
    org_id: str,
    cohort_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = CohortService(db)
    cohort = await svc.get_cohort(cohort_id)
    if cohort.org_id != org_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    assignments = await svc.list_assigned_projects(cohort_id)
    return DataResponse(
        data=[
            CohortProjectAssignmentResponse(
                **CohortProjectAssignmentResponse.model_validate(a).model_dump()
                | {"project_title": title}
            )
            for a, title in assignments
        ]
    )


# ── Dashboard / Progress ─────────────────────────────────


@router.get("/orgs/{org_id}/cohorts/{cohort_id}/progress", response_model=DataResponse[dict], dependencies=[Depends(rate_limit(20, 60))])
async def cohort_progress(
    org_id: str,
    cohort_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instructor dashboard: aggregate progress metrics for a cohort."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    data = await svc.get_cohort_progress(cohort_id, org_id)
    return DataResponse(data=data)


@router.get(
    "/orgs/{org_id}/cohorts/{cohort_id}/progress/{user_id}",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def learner_drill_down(
    org_id: str,
    cohort_id: str,
    user_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instructor view: a specific learner's progress within a cohort."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = CohortService(db)
    data = await svc.get_learner_drill_down(cohort_id, user_id, org_id)
    return DataResponse(data=data)


@router.get(
    "/orgs/{org_id}/cohorts/{cohort_id}/my-dashboard",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def my_cohort_dashboard(
    org_id: str,
    cohort_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Learner's own view within a cohort: assigned skills, projects, deadlines."""
    await require_org_member(org_id, user, db)
    svc = CohortService(db)
    data = await svc.get_learner_dashboard(cohort_id, user.id, org_id)
    return DataResponse(data=data)


# ── Learner: My Cohorts ──────────────────────────────────


@router.get("/orgs/{org_id}/my-cohorts", response_model=DataResponse[list[CohortResponse]], dependencies=[Depends(rate_limit(20, 60))])
async def my_cohorts(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List cohorts the current user belongs to within this org."""
    await require_org_member(org_id, user, db)
    from sqlalchemy import select as _sel

    from app.models.cohort import Cohort, CohortMember, CohortStatus

    result = await db.execute(
        _sel(Cohort)
        .join(CohortMember, CohortMember.cohort_id == Cohort.id)
        .where(
            Cohort.org_id == org_id,
            CohortMember.user_id == user.id,
            Cohort.status != CohortStatus.ARCHIVED,
        )
        .order_by(Cohort.created_at.desc())
    )
    cohorts = list(result.scalars().all())
    svc = CohortService(db)
    items = []
    for co in cohorts:
        count = await svc.get_member_count(co.id)
        items.append(_cohort_response(co, count))
    return DataResponse(data=items)

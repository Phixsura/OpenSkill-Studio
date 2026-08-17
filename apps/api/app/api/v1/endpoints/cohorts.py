"""Cohort management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
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


@router.post("/orgs/{org_id}/cohorts", response_model=DataResponse[CohortResponse], status_code=201)
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


@router.get("/orgs/{org_id}/cohorts", response_model=ListResponse[CohortResponse])
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


@router.get("/orgs/{org_id}/cohorts/{cohort_id}", response_model=DataResponse[CohortResponse])
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


@router.put("/orgs/{org_id}/cohorts/{cohort_id}", response_model=DataResponse[CohortResponse])
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


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}", status_code=204)
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
    role = CohortRole(body.role)
    for uid in body.user_ids:
        try:
            await svc.add_member(cohort_id, uid, role, org_id)
            enrolled += 1
        except Exception:  # noqa: BLE001 — skip duplicates/errors
            skipped += 1
    await db.commit()
    return DataResponse(data={"enrolled": enrolled, "skipped": skipped})


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}/members/{user_id}", status_code=204)
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


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}/skills/{skill_id}", status_code=204)
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


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}/projects/{project_id}", status_code=204)
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

"""Learning Path endpoints — CRUD, items, cohort assignment, progress."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.skill import ContentStatus
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.learning_path import (
    AddPathItemRequest,
    AssignPathRequest,
    CreateLearningPathRequest,
    LearningPathResponse,
    PathItemResponse,
    UpdateLearningPathRequest,
)
from app.services.learning_path import LearningPathService

router = APIRouter(tags=["Learning Paths"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Path CRUD ──


@router.post("/orgs/{org_id}/paths", response_model=DataResponse[LearningPathResponse], status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def create_path(
    org_id: str, body: CreateLearningPathRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    path = await svc.create_path(org_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=LearningPathResponse.model_validate(path))


@router.get("/orgs/{org_id}/paths", response_model=ListResponse[LearningPathResponse], dependencies=[Depends(rate_limit(20, 60))])
async def list_paths(
    org_id: str, page: int = Query(default=1, ge=1), per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = LearningPathService(db)
    paths, total = await svc.list_paths(org_id, page, per_page)
    return ListResponse(
        data=[LearningPathResponse.model_validate(p) for p in paths],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get("/orgs/{org_id}/paths/{path_id}", response_model=DataResponse[LearningPathResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_path(
    org_id: str, path_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = LearningPathService(db)
    path = await svc.get_path(path_id, org_id)
    return DataResponse(data=LearningPathResponse.model_validate(path))


@router.put("/orgs/{org_id}/paths/{path_id}", response_model=DataResponse[LearningPathResponse], dependencies=[Depends(rate_limit(20, 60))])
async def update_path(
    org_id: str, path_id: str, body: UpdateLearningPathRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    updates = body.model_dump(exclude_none=True)
    # Convert status string to ContentStatus
    if "status" in updates:
        updates["status"] = ContentStatus(updates["status"].lower())
    path = await svc.update_path(path_id, org_id, **updates)
    await db.commit()
    return DataResponse(data=LearningPathResponse.model_validate(path))


@router.delete("/orgs/{org_id}/paths/{path_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def delete_path(
    org_id: str, path_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    await svc.delete_path(path_id, org_id)
    await db.commit()


# ── Items ──


@router.post("/orgs/{org_id}/paths/{path_id}/items", response_model=DataResponse[PathItemResponse], status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def add_item(
    org_id: str, path_id: str, body: AddPathItemRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    item = await svc.add_item(path_id, org_id, **body.model_dump())
    await db.commit()
    return DataResponse(data=PathItemResponse.model_validate(item))


@router.delete("/orgs/{org_id}/paths/{path_id}/items/{item_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def remove_item(
    org_id: str, path_id: str, item_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    await svc.remove_item(item_id, path_id, org_id)
    await db.commit()


@router.get("/orgs/{org_id}/paths/{path_id}/items", response_model=DataResponse[list[PathItemResponse]], dependencies=[Depends(rate_limit(20, 60))])
async def list_items(
    org_id: str, path_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = LearningPathService(db)
    await svc.get_path(path_id, org_id)
    items = await svc.list_items(path_id)
    return DataResponse(data=[PathItemResponse.model_validate(i) for i in items])


# ── Cohort Assignment ──


@router.post("/orgs/{org_id}/cohorts/{cohort_id}/paths", status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def assign_path_to_cohort(
    org_id: str, cohort_id: str, body: AssignPathRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    await svc.assign_to_cohort(body.path_id, cohort_id, org_id, user.id)
    await db.commit()
    return DataResponse(data={"cohort_id": cohort_id, "path_id": body.path_id})


@router.delete("/orgs/{org_id}/cohorts/{cohort_id}/paths/{path_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def unassign_path(
    org_id: str, cohort_id: str, path_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    await svc.unassign_from_cohort(path_id, cohort_id, org_id)
    await db.commit()


@router.get("/orgs/{org_id}/cohorts/{cohort_id}/paths", response_model=DataResponse[list[dict]], dependencies=[Depends(rate_limit(20, 60))])
async def list_cohort_paths(
    org_id: str, cohort_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = LearningPathService(db)
    assignments = await svc.list_cohort_paths(cohort_id, org_id)
    return DataResponse(data=[
        {"cohort_id": cohort_id, "path_id": a.path_id, "path_name": name, "assigned_at": a.assigned_at.isoformat()}
        for a, name in assignments
    ])


# ── Progress ──


@router.get("/orgs/{org_id}/paths/{path_id}/my-progress", response_model=DataResponse[dict], dependencies=[Depends(rate_limit(20, 60))])
async def my_path_progress(
    org_id: str, path_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = LearningPathService(db)
    await svc.get_path(path_id, org_id)
    progress = await svc.get_path_progress(path_id, user.id, org_id)
    # Commit because get_path_progress may issue certificates and award points
    await db.commit()
    return DataResponse(data=progress)


# ── Effective Skills ──


@router.get("/orgs/{org_id}/cohorts/{cohort_id}/effective-skills", response_model=DataResponse[list[str]], dependencies=[Depends(rate_limit(20, 60))])
async def effective_skills(
    org_id: str, cohort_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    """Return de-duplicated skill IDs from direct assignments + learning path assignments."""
    await require_org_member(org_id, user, db)
    svc = LearningPathService(db)
    skills = await svc.get_effective_skills(cohort_id, org_id)
    return DataResponse(data=skills)


# ── Cohort Path Progress (instructor view) ──


@router.get("/orgs/{org_id}/cohorts/{cohort_id}/paths/{path_id}/progress", response_model=DataResponse[list[dict]], dependencies=[Depends(rate_limit(20, 60))])
async def cohort_path_progress(
    org_id: str, cohort_id: str, path_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    """Instructor view: per-learner progress on a specific learning path within a cohort."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = LearningPathService(db)
    progress = await svc.get_cohort_path_progress(path_id, cohort_id, org_id)
    return DataResponse(data=progress)

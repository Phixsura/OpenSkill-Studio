"""Client brief endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.client_brief import (
    ClientBriefResponse,
    ConvertBriefToProjectRequest,
    CreateClientBriefRequest,
    UpdateClientBriefRequest,
)
from app.schemas.project import ProjectResponse
from app.services.client_brief import ClientBriefService

router = APIRouter(tags=["Client Briefs"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


@router.post(
    "/orgs/{org_id}/briefs", response_model=DataResponse[ClientBriefResponse], status_code=201
)
async def create_brief(
    org_id: str,
    body: CreateClientBriefRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    brief = await svc.create_brief(org_id, user.id, **body.model_dump())
    await db.commit()
    return DataResponse(data=ClientBriefResponse.model_validate(brief))


@router.get("/orgs/{org_id}/briefs", response_model=ListResponse[ClientBriefResponse])
async def list_briefs(
    org_id: str,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    briefs, total = await svc.list_briefs(org_id, status, page, per_page)
    return ListResponse(
        data=[ClientBriefResponse.model_validate(b) for b in briefs],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get("/orgs/{org_id}/briefs/{brief_id}", response_model=DataResponse[ClientBriefResponse])
async def get_brief(
    org_id: str,
    brief_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")
    return DataResponse(data=ClientBriefResponse.model_validate(brief))


@router.put("/orgs/{org_id}/briefs/{brief_id}", response_model=DataResponse[ClientBriefResponse])
async def update_brief(
    org_id: str,
    brief_id: str,
    body: UpdateClientBriefRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")
    brief = await svc.update_brief(brief_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ClientBriefResponse.model_validate(brief))


@router.delete("/orgs/{org_id}/briefs/{brief_id}", status_code=204)
async def delete_brief(
    org_id: str,
    brief_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    brief = await svc.get_brief(brief_id)
    if brief.org_id != org_id:
        raise HTTPException(status_code=404, detail="Brief not found")
    await svc.delete_brief(brief_id)
    await db.commit()


@router.post(
    "/orgs/{org_id}/briefs/{brief_id}/convert",
    response_model=DataResponse[ProjectResponse],
    status_code=201,
)
async def convert_brief_to_project(
    org_id: str,
    brief_id: str,
    body: ConvertBriefToProjectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = ClientBriefService(db)
    project = await svc.convert_to_project(
        brief_id,
        org_id,
        user.id,
        title=body.title,
        cohort_id=body.cohort_id,
        deadline=body.deadline,
        late_deadline=body.late_deadline,
        max_submissions=body.max_submissions,
        rubric=body.rubric,
    )
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(project))

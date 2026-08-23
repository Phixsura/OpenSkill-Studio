"""One-click duplicate endpoints for skills and projects."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.project import ProjectResponse
from app.schemas.skill import SkillResponse
from app.services.duplicate import DuplicateService

router = APIRouter(tags=["Duplicate"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


@router.post(
    "/orgs/{org_id}/skills/{skill_id}/duplicate",
    response_model=DataResponse[SkillResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def duplicate_skill(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Duplicate a skill and its exercises within the same org."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = DuplicateService(db)
    new_skill = await svc.duplicate_skill(org_id, skill_id, user.id)
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(new_skill))


@router.post(
    "/orgs/{org_id}/projects/{project_id}/duplicate",
    response_model=DataResponse[ProjectResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def duplicate_project(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Duplicate a project and its deliverables within the same org."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = DuplicateService(db)
    new_project = await svc.duplicate_project(org_id, project_id, user.id)
    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(new_project))

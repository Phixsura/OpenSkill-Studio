"""One-click duplicate endpoints for skills and projects."""

import re
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.project import (
    Project,
    ProjectDeliverable,
)
from app.models.skill import (
    ContentStatus,
    Exercise,
    Skill,
)
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.project import ProjectResponse
from app.schemas.skill import SkillResponse

router = APIRouter(tags=["Duplicate"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


def _dup_slug(slug: str) -> str:
    """Generate a copy slug: append '-copy-<hex>'."""
    base = re.sub(r"-copy-[a-f0-9]+$", "", slug)
    return f"{base}-copy-{secrets.token_hex(3)}"[:200]


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

    skill = await db.get(Skill, skill_id)
    if skill is None or skill.org_id != org_id or skill.status == ContentStatus.ARCHIVED:
        raise HTTPException(status_code=404, detail="Skill not found")

    new_skill = Skill(
        org_id=org_id,
        category_id=skill.category_id,
        name=f"{skill.name} (Copy)",
        slug=_dup_slug(skill.slug),
        description=skill.description,
        learning_content=skill.learning_content,
        difficulty=skill.difficulty,
        estimated_minutes=skill.estimated_minutes,
        tags=list(skill.tags) if skill.tags else [],
        sort_order=skill.sort_order,
        status=ContentStatus.DRAFT,
        created_by=user.id,
    )
    db.add(new_skill)
    await db.flush()

    # Copy exercises
    exercises_result = await db.execute(
        select(Exercise)
        .where(Exercise.skill_id == skill_id, Exercise.status != ContentStatus.ARCHIVED)
        .order_by(Exercise.sort_order)
    )
    for ex in exercises_result.scalars().all():
        new_ex = Exercise(
            org_id=org_id,
            skill_id=new_skill.id,
            title=ex.title,
            description=ex.description,
            type=ex.type,
            config=dict(ex.config) if ex.config else {},
            sort_order=ex.sort_order,
            max_score=ex.max_score,
            status=ContentStatus.DRAFT,
            created_by=user.id,
        )
        db.add(new_ex)

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

    project = await db.get(Project, project_id)
    if project is None or project.org_id != org_id or project.status == ContentStatus.ARCHIVED:
        raise HTTPException(status_code=404, detail="Project not found")

    new_project = Project(
        org_id=org_id,
        title=f"{project.title} (Copy)",
        slug=_dup_slug(project.slug),
        description=project.description,
        instructions=project.instructions,
        project_type=project.project_type,
        difficulty=project.difficulty,
        max_score=project.max_score,
        rubric=dict(project.rubric) if isinstance(project.rubric, dict) else project.rubric,
        deadline=None,  # Don't copy deadline
        late_deadline=None,
        late_penalty_pct=project.late_penalty_pct,
        max_submissions=project.max_submissions,
        status=ContentStatus.DRAFT,
        created_by=user.id,
    )
    db.add(new_project)
    await db.flush()

    # Copy deliverables
    deliverables_result = await db.execute(
        select(ProjectDeliverable)
        .where(ProjectDeliverable.project_id == project_id)
        .order_by(ProjectDeliverable.sort_order)
    )
    for d in deliverables_result.scalars().all():
        new_d = ProjectDeliverable(
            project_id=new_project.id,
            name=d.name,
            description=d.description,
            type=d.type,
            required=d.required,
            config=dict(d.config) if d.config else {},
            sort_order=d.sort_order,
        )
        db.add(new_d)

    await db.commit()
    return DataResponse(data=ProjectResponse.model_validate(new_project))

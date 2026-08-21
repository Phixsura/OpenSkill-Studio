"""Duplication service — one-click clone of skills and projects."""

import re
import secrets

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.project import Project, ProjectDeliverable
from app.models.skill import ContentStatus, Exercise, Skill

log = structlog.get_logger()


def _dup_slug(slug: str) -> str:
    """Generate a copy slug: append '-copy-<hex>'."""
    base = re.sub(r"-copy-[a-f0-9]+$", "", slug)
    return f"{base}-copy-{secrets.token_hex(3)}"[:200]


class DuplicateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def duplicate_skill(
        self,
        org_id: str,
        skill_id: str,
        user_id: str,
    ) -> Skill:
        """Duplicate a skill and its exercises within the same org."""
        skill = await self.db.get(Skill, skill_id)
        if skill is None or skill.org_id != org_id or skill.status == ContentStatus.ARCHIVED:
            raise AppError("SKILL_NOT_FOUND", "Skill not found", 404)

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
            created_by=user_id,
        )
        self.db.add(new_skill)
        await self.db.flush()

        # Copy exercises
        exercises_result = await self.db.execute(
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
                created_by=user_id,
            )
            self.db.add(new_ex)

        await self.db.flush()
        log.info("skill_duplicated", original_id=skill_id, new_id=new_skill.id, org_id=org_id)
        return new_skill

    async def duplicate_project(
        self,
        org_id: str,
        project_id: str,
        user_id: str,
    ) -> Project:
        """Duplicate a project and its deliverables within the same org."""
        project = await self.db.get(Project, project_id)
        if project is None or project.org_id != org_id or project.status == ContentStatus.ARCHIVED:
            raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)

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
            created_by=user_id,
        )
        self.db.add(new_project)
        await self.db.flush()

        # Copy deliverables
        deliverables_result = await self.db.execute(
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
            self.db.add(new_d)

        await self.db.flush()
        log.info("project_duplicated", original_id=project_id, new_id=new_project.id, org_id=org_id)
        return new_project

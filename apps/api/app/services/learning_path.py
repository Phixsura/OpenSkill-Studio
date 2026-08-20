"""Learning Path management — CRUD, items, cohort assignment, progress."""

import re
import secrets

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.learning_path import (
    CohortLearningPathAssignment,
    LearningPath,
    LearningPathItem,
    PathItemType,
)
from app.models.project import Project, Submission, SubmissionStatus
from app.models.skill import ContentStatus, ProgressStatus, Skill, SkillProgress

log = structlog.get_logger()


class PathNotFoundError(AppError):
    def __init__(self):
        super().__init__("PATH_NOT_FOUND", "Learning path not found", 404)


class LearningPathService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD ──

    async def create_path(self, org_id: str, created_by: str, **fields) -> LearningPath:
        name = fields.get("name", "Untitled Path")
        slug = self._generate_slug(name)

        path = LearningPath(org_id=org_id, slug=slug, created_by=created_by, **fields)
        # Always add random suffix to slug to avoid IntegrityError + rollback issues
        path.slug = f"{slug[:190]}-{secrets.token_hex(3)}"
        self.db.add(path)
        await self.db.flush()

        log.info("path_created", path_id=path.id, org_id=org_id)
        return path

    async def list_paths(
        self, org_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[LearningPath], int]:
        base = select(LearningPath).where(
            LearningPath.org_id == org_id,
            LearningPath.status != ContentStatus.ARCHIVED,
        )
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(LearningPath.created_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_path(self, path_id: str, org_id: str) -> LearningPath:
        path = await self.db.get(LearningPath, path_id)
        if path is None or path.org_id != org_id or path.status == ContentStatus.ARCHIVED:
            raise PathNotFoundError()
        return path

    async def update_path(self, path_id: str, org_id: str, **fields) -> LearningPath:
        path = await self.get_path(path_id, org_id)
        if fields.get("name"):
            path.slug = self._generate_slug(fields["name"])
        for k, v in fields.items():
            if v is not None and hasattr(path, k):
                setattr(path, k, v)
        await self.db.flush()
        await self.db.refresh(path)
        return path

    async def delete_path(self, path_id: str, org_id: str) -> None:
        path = await self.get_path(path_id, org_id)
        path.status = ContentStatus.ARCHIVED
        await self.db.flush()

    # ── Items ──

    async def add_item(
        self,
        path_id: str,
        org_id: str,
        item_type: str,
        skill_id: str | None = None,
        project_id: str | None = None,
        section_title: str | None = None,
        sort_order: int = 0,
        required: bool = True,
        unlock_rule: str = "previous_required",
    ) -> LearningPathItem:
        await self.get_path(path_id, org_id)

        try:
            ptype = PathItemType(item_type.lower())
        except ValueError as exc:
            raise AppError(
                "INVALID_ITEM_TYPE",
                f"Invalid item_type '{item_type}'. Must be one of: skill, project, section",
                422,
            ) from exc

        # Validate references
        if ptype == PathItemType.SKILL:
            if not skill_id:
                raise AppError("MISSING_SKILL_ID", "skill_id required for skill items", 422)
            skill = await self.db.get(Skill, skill_id)
            if skill is None or skill.org_id != org_id:
                raise AppError("SKILL_NOT_FOUND", "Skill not found in this org", 404)
        elif ptype == PathItemType.PROJECT:
            if not project_id:
                raise AppError("MISSING_PROJECT_ID", "project_id required for project items", 422)
            project = await self.db.get(Project, project_id)
            if project is None or project.org_id != org_id:
                raise AppError("PROJECT_NOT_FOUND", "Project not found in this org", 404)
        elif ptype == PathItemType.SECTION:
            if not section_title:
                raise AppError("MISSING_TITLE", "section_title required for section items", 422)

        item = LearningPathItem(
            path_id=path_id,
            item_type=ptype,
            skill_id=skill_id if ptype == PathItemType.SKILL else None,
            project_id=project_id if ptype == PathItemType.PROJECT else None,
            section_title=section_title if ptype == PathItemType.SECTION else None,
            sort_order=sort_order,
            required=required,
            unlock_rule=unlock_rule,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def remove_item(self, item_id: str, path_id: str, org_id: str) -> None:
        await self.get_path(path_id, org_id)
        item = await self.db.get(LearningPathItem, item_id)
        if item is None or item.path_id != path_id:
            raise AppError("ITEM_NOT_FOUND", "Item not found in this path", 404)
        await self.db.delete(item)
        await self.db.flush()

    async def list_items(self, path_id: str) -> list[LearningPathItem]:
        result = await self.db.execute(
            select(LearningPathItem)
            .where(LearningPathItem.path_id == path_id)
            .order_by(LearningPathItem.sort_order)
        )
        return list(result.scalars().all())

    # ── Cohort Assignment ──

    async def _verify_cohort_org(self, cohort_id: str, org_id: str) -> None:
        """Verify the cohort belongs to the same org (prevents cross-tenant IDOR)."""
        from app.models.cohort import Cohort

        cohort = await self.db.get(Cohort, cohort_id)
        if cohort is None or cohort.org_id != org_id:
            raise AppError("COHORT_NOT_FOUND", "Cohort not found in this organization", 404)

    async def assign_to_cohort(
        self, path_id: str, cohort_id: str, org_id: str, assigned_by: str
    ) -> None:
        await self._verify_cohort_org(cohort_id, org_id)
        path = await self.get_path(path_id, org_id)
        if path.status != ContentStatus.PUBLISHED:
            raise AppError("PATH_NOT_PUBLISHED", "Only published paths can be assigned", 422)

        assignment = CohortLearningPathAssignment(
            cohort_id=cohort_id,
            path_id=path_id,
            assigned_by=assigned_by,
        )
        self.db.add(assignment)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError("ALREADY_ASSIGNED", "Path already assigned to this cohort", 409) from None

    async def unassign_from_cohort(self, path_id: str, cohort_id: str, org_id: str) -> None:
        await self._verify_cohort_org(cohort_id, org_id)
        await self.get_path(path_id, org_id)
        result = await self.db.execute(
            select(CohortLearningPathAssignment).where(
                CohortLearningPathAssignment.cohort_id == cohort_id,
                CohortLearningPathAssignment.path_id == path_id,
            )
        )
        assignment = result.scalar_one_or_none()
        if assignment is None:
            raise AppError("NOT_ASSIGNED", "Path not assigned to this cohort", 404)
        await self.db.delete(assignment)
        await self.db.flush()

    async def list_cohort_paths(self, cohort_id: str, org_id: str) -> list[tuple[CohortLearningPathAssignment, str]]:
        await self._verify_cohort_org(cohort_id, org_id)
        result = await self.db.execute(
            select(CohortLearningPathAssignment, LearningPath.name)
            .join(LearningPath, LearningPath.id == CohortLearningPathAssignment.path_id)
            .where(
                CohortLearningPathAssignment.cohort_id == cohort_id,
                LearningPath.status != ContentStatus.ARCHIVED,
            )
        )
        return [(row[0], row[1]) for row in result.all()]

    # ── Progress ──

    async def get_path_progress(self, path_id: str, user_id: str, org_id: str) -> dict:
        items = await self.list_items(path_id)
        result_items = []
        completed = 0
        total_required = 0
        all_prev_done = True

        for item in items:
            if item.item_type == PathItemType.SECTION:
                result_items.append({
                    "type": "section",
                    "title": item.section_title,
                })
                continue

            is_required = item.required
            if is_required:
                total_required += 1

            is_done = False
            name = ""

            if item.item_type == PathItemType.SKILL and item.skill_id:
                skill = await self.db.get(Skill, item.skill_id)
                name = skill.name if skill else "Unknown"
                progress_r = await self.db.execute(
                    select(SkillProgress).where(
                        SkillProgress.skill_id == item.skill_id,
                        SkillProgress.user_id == user_id,
                    )
                )
                progress = progress_r.scalar_one_or_none()
                is_done = progress is not None and progress.status == ProgressStatus.COMPLETED

            elif item.item_type == PathItemType.PROJECT and item.project_id:
                project = await self.db.get(Project, item.project_id)
                name = project.title if project else "Unknown"
                sub_r = await self.db.execute(
                    select(Submission).where(
                        Submission.project_id == item.project_id,
                        Submission.user_id == user_id,
                        Submission.status == SubmissionStatus.APPROVED,
                    ).limit(1)
                )
                is_done = sub_r.scalar_one_or_none() is not None

            # Unlock logic
            is_locked = False if item.unlock_rule == "immediate" else not all_prev_done

            if is_done and is_required:
                completed += 1

            status = "completed" if is_done else ("locked" if is_locked else "available")

            result_items.append({
                "type": item.item_type.value,
                "item_id": item.id,
                "skill_id": item.skill_id,
                "project_id": item.project_id,
                "name": name,
                "required": is_required,
                "status": status,
            })

            if is_required:
                all_prev_done = all_prev_done and is_done

        pct = round(completed * 100 / total_required) if total_required > 0 else 100

        # Issue certificate on 100% completion
        certificate_number = None
        if pct == 100:
            certificate_number = await self._maybe_issue_certificate(
                path_id, user_id, org_id, completed
            )

        result = {
            "path_id": path_id,
            "items": result_items,
            "completed": completed,
            "total_required": total_required,
            "pct": pct,
        }
        if certificate_number:
            result["certificate_number"] = certificate_number
        return result

    # ── Certificates ──

    async def _maybe_issue_certificate(
        self, path_id: str, user_id: str, org_id: str, skills_completed: int
    ) -> str | None:
        """Issue a completion certificate if one doesn't already exist.

        Populates the certificate data JSONB with actual skill/project names
        from the path items so the certificate endpoint returns meaningful info.
        """
        import uuid

        from app.models.certificate import Certificate
        from app.models.organization import Organization
        from app.models.user import User

        existing_r = await self.db.execute(
            select(Certificate).where(
                Certificate.user_id == user_id,
                Certificate.path_id == path_id,
            )
        )
        existing = existing_r.scalar_one_or_none()
        if existing:
            return existing.certificate_number

        path = await self.db.get(LearningPath, path_id)
        user = await self.db.get(User, user_id)
        org = await self.db.get(Organization, org_id)

        # Collect actual skill/project names from path items
        items = await self.list_items(path_id)
        skills_data: list[dict] = []
        projects_data: list[dict] = []

        for item in items:
            if item.item_type == PathItemType.SKILL and item.skill_id:
                skill = await self.db.get(Skill, item.skill_id)
                if skill:
                    skills_data.append({
                        "skill_id": skill.id,
                        "name": skill.name,
                    })
            elif item.item_type == PathItemType.PROJECT and item.project_id:
                project = await self.db.get(Project, item.project_id)
                if project:
                    projects_data.append({
                        "project_id": project.id,
                        "name": project.title,
                    })

        cert_number = str(uuid.uuid4())
        cert = Certificate(
            user_id=user_id,
            path_id=path_id,
            org_id=org_id,
            certificate_number=cert_number,
            data={
                "user_name": user.display_name if user else "Unknown",
                "path_name": path.name if path else "Unknown",
                "org_name": org.name if org else "Unknown",
                "skills_completed": skills_completed,
                "skills": skills_data,
                "projects": projects_data,
            },
        )
        self.db.add(cert)
        await self.db.flush()

        log.info("certificate_issued", cert_number=cert_number, user_id=user_id, path_id=path_id)
        return cert_number

    # ── Effective Skills (de-duplicated) ──

    async def get_effective_skills(self, cohort_id: str, org_id: str) -> list[str]:
        """Return de-duplicated skill IDs from direct assignments + learning path assignments.

        A skill that is both directly assigned to a cohort AND part of a learning
        path assigned to the same cohort should appear only once.
        """
        from app.models.cohort import CohortSkillAssignment

        await self._verify_cohort_org(cohort_id, org_id)

        # Get directly assigned skill IDs
        direct_r = await self.db.execute(
            select(CohortSkillAssignment.skill_id).where(
                CohortSkillAssignment.cohort_id == cohort_id,
            )
        )
        direct_ids = set(direct_r.scalars().all())

        # Get skill IDs from learning path assignments
        path_assignments_r = await self.db.execute(
            select(CohortLearningPathAssignment.path_id).where(
                CohortLearningPathAssignment.cohort_id == cohort_id,
            )
        )
        path_ids = list(path_assignments_r.scalars().all())

        path_skill_ids: set[str] = set()
        for pid in path_ids:
            items_r = await self.db.execute(
                select(LearningPathItem.skill_id).where(
                    LearningPathItem.path_id == pid,
                    LearningPathItem.item_type == PathItemType.SKILL,
                    LearningPathItem.skill_id.is_not(None),
                )
            )
            path_skill_ids.update(items_r.scalars().all())

        # Union and deduplicate
        all_skills = direct_ids | path_skill_ids
        return list(all_skills)

    # ── Cohort Path Progress (instructor view) ──

    async def get_cohort_path_progress(
        self, path_id: str, cohort_id: str, org_id: str
    ) -> list[dict]:
        """Return per-learner progress on a path for all learners in a cohort.

        Used by instructors to see how each learner is progressing through
        a specific learning path assigned to the cohort.
        """
        from app.models.cohort import CohortMember, CohortRole

        await self._verify_cohort_org(cohort_id, org_id)
        await self.get_path(path_id, org_id)

        # Get all learners in the cohort
        learners_r = await self.db.execute(
            select(CohortMember).where(
                CohortMember.cohort_id == cohort_id,
                CohortMember.role == CohortRole.LEARNER,
            )
        )
        learners = list(learners_r.scalars().all())

        # For each learner, compute their path progress
        results: list[dict] = []
        for member in learners:
            progress = await self.get_path_progress(path_id, member.user_id, org_id)
            results.append({
                "user_id": member.user_id,
                "completed": progress["completed"],
                "total_required": progress["total_required"],
                "pct": progress["pct"],
            })

        return results

    # ── Helpers ──

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]

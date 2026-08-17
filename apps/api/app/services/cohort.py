"""Cohort management service."""

import re
import secrets

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.cohort import (
    Cohort,
    CohortMember,
    CohortProjectAssignment,
    CohortRole,
    CohortSkillAssignment,
    CohortStatus,
    ParticipationMode,
)
from app.models.organization import MemberStatus, OrgMember
from app.models.project import Project
from app.models.skill import ContentStatus, Skill
from app.models.user import User

log = structlog.get_logger()


# ── Errors ────────────────────────────────────────────────


class CohortNotFoundError(AppError):
    def __init__(self):
        super().__init__("COHORT_NOT_FOUND", "Cohort not found", 404)


class AlreadyCohortMemberError(AppError):
    def __init__(self):
        super().__init__("ALREADY_ENROLLED", "User is already enrolled in this cohort", 409)


class CohortFullError(AppError):
    def __init__(self, max_learners: int):
        super().__init__("COHORT_FULL", f"Cohort is full (max {max_learners} learners)", 422)


# ── Service ──────────────────────────────────────────────


class CohortService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD ──

    async def create_cohort(
        self,
        org_id: str,
        name: str,
        description: str | None,
        starts_at=None,
        ends_at=None,
        max_learners: int | None = None,
        created_by: str = "",
    ) -> Cohort:
        slug = self._generate_slug(name)
        cohort = Cohort(
            org_id=org_id,
            name=name,
            slug=slug,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            max_learners=max_learners,
            created_by=created_by,
        )
        self.db.add(cohort)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            cohort.slug = f"{slug[:190]}-{secrets.token_hex(3)}"
            self.db.add(cohort)
            await self.db.flush()

        log.info("cohort_created", cohort_id=cohort.id, org_id=org_id)
        return cohort

    async def list_cohorts(
        self,
        org_id: str,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Cohort], int]:
        base = select(Cohort).where(Cohort.org_id == org_id)
        if status:
            try:
                base = base.where(Cohort.status == CohortStatus(status))
            except ValueError as exc:
                raise AppError("INVALID_FILTER", f"Invalid status: {status}", 422) from exc
        else:
            base = base.where(Cohort.status != CohortStatus.ARCHIVED)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(Cohort.created_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_cohort(self, cohort_id: str) -> Cohort:
        cohort = await self.db.get(Cohort, cohort_id)
        if cohort is None or cohort.status == CohortStatus.ARCHIVED:
            raise CohortNotFoundError()
        return cohort

    async def update_cohort(self, cohort_id: str, **fields) -> Cohort:
        cohort = await self.get_cohort(cohort_id)
        if fields.get("status"):
            cohort.status = CohortStatus(fields.pop("status"))
        if fields.get("name"):
            cohort.slug = self._generate_slug(fields["name"])
        for k, v in fields.items():
            if v is not None and hasattr(cohort, k):
                setattr(cohort, k, v)
        await self.db.flush()
        await self.db.refresh(cohort)
        return cohort

    async def delete_cohort(self, cohort_id: str) -> None:
        cohort = await self.get_cohort(cohort_id)
        if cohort.status != CohortStatus.DRAFT:
            raise AppError("INVALID_STATE", "Only draft cohorts can be deleted", 422)
        cohort.status = CohortStatus.ARCHIVED
        await self.db.flush()

    # ── Members ──

    async def add_member(
        self, cohort_id: str, user_id: str, role: CohortRole, org_id: str
    ) -> CohortMember:
        cohort = await self.get_cohort(cohort_id)
        if cohort.org_id != org_id:
            raise CohortNotFoundError()

        # User must be an active org member
        org_member = await self.db.execute(
            select(OrgMember.id).where(
                OrgMember.org_id == org_id,
                OrgMember.user_id == user_id,
                OrgMember.status == MemberStatus.ACTIVE,
            )
        )
        if org_member.scalar_one_or_none() is None:
            raise AppError("USER_NOT_FOUND", "User is not a member of this organization", 404)

        # Check max_learners
        if role == CohortRole.LEARNER and cohort.max_learners is not None:
            count_r = await self.db.execute(
                select(func.count(CohortMember.id)).where(
                    CohortMember.cohort_id == cohort_id,
                    CohortMember.role == CohortRole.LEARNER,
                )
            )
            if count_r.scalar_one() >= cohort.max_learners:
                raise CohortFullError(cohort.max_learners)

        member = CohortMember(
            cohort_id=cohort_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(member)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AlreadyCohortMemberError() from None

        log.info("cohort_member_added", cohort_id=cohort_id, user_id=user_id, role=role.value)
        return member

    async def remove_member(self, cohort_id: str, user_id: str, org_id: str) -> None:
        cohort = await self.get_cohort(cohort_id)
        if cohort.org_id != org_id:
            raise CohortNotFoundError()
        result = await self.db.execute(
            select(CohortMember).where(
                CohortMember.cohort_id == cohort_id,
                CohortMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if member is None:
            raise AppError("MEMBER_NOT_FOUND", "User is not in this cohort", 404)
        await self.db.delete(member)
        await self.db.flush()

    async def list_members(
        self,
        cohort_id: str,
        role: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[tuple[CohortMember, str | None, str | None]], int]:
        """List members with display names. Returns (member, name, email) tuples."""
        base = (
            select(CohortMember, User.display_name, User.email)
            .join(User, User.id == CohortMember.user_id, isouter=True)
            .where(CohortMember.cohort_id == cohort_id)
        )
        if role:
            try:
                base = base.where(CohortMember.role == CohortRole(role))
            except ValueError as exc:
                raise AppError("INVALID_FILTER", f"Invalid role: {role}", 422) from exc

        count_base = select(func.count(CohortMember.id)).where(CohortMember.cohort_id == cohort_id)
        if role:
            count_base = count_base.where(CohortMember.role == CohortRole(role))
        total_r = await self.db.execute(count_base)
        total = total_r.scalar_one()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(CohortMember.joined_at).offset(offset).limit(per_page)
        )
        return [(row[0], row[1], row[2]) for row in result.all()], total

    async def get_member_count(self, cohort_id: str) -> int:
        r = await self.db.execute(
            select(func.count(CohortMember.id)).where(CohortMember.cohort_id == cohort_id)
        )
        return r.scalar_one()

    # ── Skill Assignment ──

    async def assign_skill(
        self, cohort_id: str, skill_id: str, org_id: str, assigned_by: str
    ) -> CohortSkillAssignment:
        cohort = await self.get_cohort(cohort_id)
        if cohort.org_id != org_id:
            raise CohortNotFoundError()

        # Skill must exist in same org and be non-archived
        skill = await self.db.get(Skill, skill_id)
        if skill is None or skill.org_id != org_id or skill.status == ContentStatus.ARCHIVED:
            raise AppError("SKILL_NOT_FOUND", "Skill not found in this organization", 404)

        assignment = CohortSkillAssignment(
            cohort_id=cohort_id,
            skill_id=skill_id,
            assigned_by=assigned_by,
        )
        self.db.add(assignment)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError(
                "ALREADY_ASSIGNED", "Skill already assigned to this cohort", 409
            ) from None
        return assignment

    async def unassign_skill(self, cohort_id: str, skill_id: str, org_id: str) -> None:
        cohort = await self.get_cohort(cohort_id)
        if cohort.org_id != org_id:
            raise CohortNotFoundError()
        result = await self.db.execute(
            select(CohortSkillAssignment).where(
                CohortSkillAssignment.cohort_id == cohort_id,
                CohortSkillAssignment.skill_id == skill_id,
            )
        )
        assignment = result.scalar_one_or_none()
        if assignment is None:
            raise AppError("ASSIGNMENT_NOT_FOUND", "Skill not assigned to this cohort", 404)
        await self.db.delete(assignment)
        await self.db.flush()

    async def list_assigned_skills(self, cohort_id: str) -> list[tuple[CohortSkillAssignment, str]]:
        """List assigned skills with names."""
        result = await self.db.execute(
            select(CohortSkillAssignment, Skill.name)
            .join(Skill, Skill.id == CohortSkillAssignment.skill_id)
            .where(CohortSkillAssignment.cohort_id == cohort_id)
            .order_by(Skill.name)
        )
        return [(row[0], row[1]) for row in result.all()]

    # ── Project Assignment ──

    async def assign_project(
        self,
        cohort_id: str,
        project_id: str,
        org_id: str,
        assigned_by: str,
        deadline_override=None,
        late_deadline_override=None,
        max_submissions_override: int | None = None,
        participation_mode: str = "assigned",
    ) -> CohortProjectAssignment:
        cohort = await self.get_cohort(cohort_id)
        if cohort.org_id != org_id:
            raise CohortNotFoundError()

        project = await self.db.get(Project, project_id)
        if project is None or project.org_id != org_id:
            raise AppError("PROJECT_NOT_FOUND", "Project not found in this organization", 404)

        try:
            mode = ParticipationMode(participation_mode)
        except ValueError:
            mode = ParticipationMode.ASSIGNED

        assignment = CohortProjectAssignment(
            cohort_id=cohort_id,
            project_id=project_id,
            deadline_override=deadline_override,
            late_deadline_override=late_deadline_override,
            max_submissions_override=max_submissions_override,
            participation_mode=mode,
            assigned_by=assigned_by,
        )
        self.db.add(assignment)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError(
                "ALREADY_ASSIGNED", "Project already assigned to this cohort", 409
            ) from None
        return assignment

    async def unassign_project(self, cohort_id: str, project_id: str, org_id: str) -> None:
        cohort = await self.get_cohort(cohort_id)
        if cohort.org_id != org_id:
            raise CohortNotFoundError()
        result = await self.db.execute(
            select(CohortProjectAssignment).where(
                CohortProjectAssignment.cohort_id == cohort_id,
                CohortProjectAssignment.project_id == project_id,
            )
        )
        assignment = result.scalar_one_or_none()
        if assignment is None:
            raise AppError("ASSIGNMENT_NOT_FOUND", "Project not assigned to this cohort", 404)
        await self.db.delete(assignment)
        await self.db.flush()

    async def list_assigned_projects(
        self, cohort_id: str
    ) -> list[tuple[CohortProjectAssignment, str]]:
        """List assigned projects with titles."""
        result = await self.db.execute(
            select(CohortProjectAssignment, Project.title)
            .join(Project, Project.id == CohortProjectAssignment.project_id)
            .where(CohortProjectAssignment.cohort_id == cohort_id)
            .order_by(CohortProjectAssignment.assigned_at)
        )
        return [(row[0], row[1]) for row in result.all()]

    # ── Helpers ──

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]

"""Client brief management service."""

import re
import secrets
from datetime import datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.client_brief import BriefStatus, ClientBrief

log = structlog.get_logger()


# ── Errors ────────────────────────────────────────────────


class BriefNotFoundError(AppError):
    def __init__(self):
        super().__init__("BRIEF_NOT_FOUND", "Client brief not found", 404)


# ── Service ──────────────────────────────────────────────


class ClientBriefService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_brief(
        self,
        org_id: str,
        created_by: str,
        **fields,
    ) -> ClientBrief:
        title = fields.get("title", "Untitled Brief")
        slug = self._generate_slug(title)

        brief = ClientBrief(
            org_id=org_id,
            slug=slug,
            created_by=created_by,
            **fields,
        )
        self.db.add(brief)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            brief.slug = f"{slug[:290]}-{secrets.token_hex(3)}"
            self.db.add(brief)
            await self.db.flush()

        log.info("brief_created", brief_id=brief.id, org_id=org_id)
        return brief

    async def list_briefs(
        self,
        org_id: str,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[ClientBrief], int]:
        base = select(ClientBrief).where(ClientBrief.org_id == org_id)
        if status:
            try:
                base = base.where(ClientBrief.status == BriefStatus(status))
            except ValueError as exc:
                raise AppError("INVALID_FILTER", f"Invalid status: {status}", 422) from exc
        else:
            base = base.where(ClientBrief.status != BriefStatus.ARCHIVED)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(ClientBrief.created_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_brief(self, brief_id: str) -> ClientBrief:
        brief = await self.db.get(ClientBrief, brief_id)
        if brief is None or brief.status == BriefStatus.ARCHIVED:
            raise BriefNotFoundError()
        return brief

    # Valid status transitions for client briefs
    _VALID_TRANSITIONS: dict[BriefStatus, set[BriefStatus]] = {
        BriefStatus.DRAFT: {BriefStatus.OPEN, BriefStatus.CANCELLED},
        BriefStatus.OPEN: {BriefStatus.ASSIGNED, BriefStatus.CANCELLED},
        BriefStatus.ASSIGNED: {BriefStatus.IN_PRODUCTION, BriefStatus.CANCELLED},
        BriefStatus.IN_PRODUCTION: {BriefStatus.REVIEW, BriefStatus.CANCELLED},
        BriefStatus.REVIEW: {BriefStatus.COMPLETED, BriefStatus.CANCELLED},
        BriefStatus.COMPLETED: {BriefStatus.ARCHIVED},
        BriefStatus.ACTIVE: {BriefStatus.COMPLETED, BriefStatus.CANCELLED},
        BriefStatus.CANCELLED: {BriefStatus.ARCHIVED},
    }

    async def update_brief(self, brief_id: str, **fields) -> ClientBrief:
        brief = await self.get_brief(brief_id)
        if fields.get("status"):
            new_status = BriefStatus(fields.pop("status"))
            allowed = self._VALID_TRANSITIONS.get(brief.status, set())
            if new_status not in allowed:
                raise AppError(
                    "INVALID_TRANSITION",
                    f"Cannot transition from {brief.status.value} to {new_status.value}",
                    422,
                )
            brief.status = new_status
        if fields.get("title"):
            brief.slug = self._generate_slug(fields["title"])
        for k, v in fields.items():
            if v is not None and hasattr(brief, k):
                setattr(brief, k, v)
        await self.db.flush()
        await self.db.refresh(brief)
        return brief

    async def delete_brief(self, brief_id: str) -> None:
        brief = await self.get_brief(brief_id)
        if brief.status != BriefStatus.DRAFT:
            raise AppError("INVALID_STATE", "Only draft briefs can be deleted", 422)
        brief.status = BriefStatus.ARCHIVED
        await self.db.flush()

    async def convert_to_project(
        self,
        brief_id: str,
        org_id: str,
        created_by: str,
        title: str | None = None,
        cohort_id: str | None = None,
        deadline: datetime | None = None,
        late_deadline: datetime | None = None,
        max_submissions: int = 0,
        rubric: list[dict] | None = None,
    ):
        """Convert a client brief into a Project.

        Reuses the existing ProjectService.create_project flow so the resulting
        project gets deliverables, skills, publish workflow — everything a
        normal project has.
        """
        from app.services.project import ProjectService

        brief = await self.get_brief(brief_id)
        if brief.org_id != org_id:
            raise BriefNotFoundError()
        # Only draft briefs can be converted — a second convert on an already-
        # active brief would create duplicate projects and crash on lazy-load.
        if brief.status != BriefStatus.DRAFT:
            raise AppError("INVALID_STATE", "Only draft briefs can be converted", 422)

        # Validate cohort belongs to the same org
        if cohort_id:
            from app.models.cohort import Cohort

            cohort = await self.db.get(Cohort, cohort_id)
            if cohort is None or cohort.org_id != org_id:
                raise AppError(
                    "INVALID_COHORT",
                    "Cohort not found in this organization",
                    404,
                )

        project_svc = ProjectService(self.db)
        project = await project_svc.create_project(
            org_id=org_id,
            title=title or brief.title,
            slug=None,
            description=brief.objective,
            instructions=f"## Client Brief: {brief.client_name}\n\n{brief.objective}",
            difficulty="intermediate",
            max_score=sum(r.get("max_score", 0) for r in (rubric or [])) or 100,
            rubric=rubric or [{"criterion": "Overall Quality", "max_score": 100}],
            deadline=deadline,
            late_deadline=late_deadline,
            late_penalty_pct=0,
            max_submissions=max_submissions,
            skill_ids=None,
            created_by=created_by,
            project_type="ai_visual",
        )
        # Link back to the brief
        project.client_brief_id = brief_id
        if cohort_id:
            project.cohort_id = cohort_id
        await self.db.flush()

        # Create deliverables from brief specs
        for i, spec in enumerate(brief.deliverable_specs or []):
            await project_svc.create_deliverable(
                project.id,
                spec.get("name", f"Deliverable {i + 1}"),
                spec.get("description"),
                spec.get("type", "file"),
                spec.get("required", True),
                spec.get("config", {}),
                i,
            )

        # Mark brief as assigned
        brief.status = BriefStatus.ACTIVE
        await self.db.flush()

        log.info(
            "brief_converted",
            brief_id=brief_id,
            project_id=project.id,
            org_id=org_id,
        )
        return project

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:300]

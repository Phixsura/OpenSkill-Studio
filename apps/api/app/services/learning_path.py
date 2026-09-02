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
            slug = self._generate_slug(fields["name"])
            path.slug = f"{slug[:190]}-{secrets.token_hex(3)}"
        for k, v in fields.items():
            if v is not None and hasattr(path, k):
                setattr(path, k, v)
        await self.db.flush()
        await self.db.refresh(path)
        return path

    async def delete_path(self, path_id: str, org_id: str) -> None:
        path = await self.get_path(path_id, org_id)
        path.status = ContentStatus.ARCHIVED

        # Clean up path items and cohort assignments
        from sqlalchemy import delete as sa_delete

        await self.db.execute(
            sa_delete(LearningPathItem).where(LearningPathItem.path_id == path_id)
        )
        await self.db.execute(
            sa_delete(CohortLearningPathAssignment).where(
                CohortLearningPathAssignment.path_id == path_id
            )
        )
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
        workflow_pack_id: str | None = None,
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
                f"Invalid item_type '{item_type}'. Must be one of: "
                "skill, project, section, workflow_pack",
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
        elif ptype == PathItemType.WORKFLOW_PACK:
            if not workflow_pack_id:
                raise AppError(
                    "MISSING_WORKFLOW_PACK_ID",
                    "workflow_pack_id required for workflow_pack items",
                    422,
                )
            # The pack must be INSTALLED in this org (an installation row is
            # the org's claim to it — a bare pack id could reference any
            # foreign private pack). Loose-coupled column, so check here.
            from app.models.skill_pack import InstallStatus
            from app.models.workflow_pack import WorkflowPackInstallation

            install_r = await self.db.execute(
                select(WorkflowPackInstallation).where(
                    WorkflowPackInstallation.org_id == org_id,
                    WorkflowPackInstallation.pack_id == workflow_pack_id,
                    WorkflowPackInstallation.status != InstallStatus.REMOVED,
                )
            )
            if install_r.scalar_one_or_none() is None:
                raise AppError(
                    "WORKFLOW_PACK_NOT_INSTALLED",
                    "Workflow pack is not installed in this organization",
                    404,
                )

        item = LearningPathItem(
            path_id=path_id,
            item_type=ptype,
            skill_id=skill_id if ptype == PathItemType.SKILL else None,
            project_id=project_id if ptype == PathItemType.PROJECT else None,
            section_title=section_title if ptype == PathItemType.SECTION else None,
            workflow_pack_id=(workflow_pack_id if ptype == PathItemType.WORKFLOW_PACK else None),
            sort_order=sort_order,
            required=required,
            unlock_rule=unlock_rule,
        )
        self.db.add(item)
        try:
            await self.db.flush()
        except IntegrityError:
            # R57[1]: when running inside an outbox-handler SAVEPOINT
            # (worker isolation, provisioning steps), session.rollback()
            # rolls back the ROOT batch transaction — poisoning every
            # sibling message and un-claiming rows mid-flight. Inside a
            # nested transaction we only raise: the enclosing
            # begin_nested() unwinds to the savepoint and the root stays
            # usable. On the plain request path behavior is unchanged.
            if not self.db.in_nested_transaction():
                await self.db.rollback()
            raise AppError(
                "REFERENCE_NOT_FOUND", "Referenced skill or project no longer exists", 404
            ) from None
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
            .order_by(LearningPathItem.sort_order, LearningPathItem.id)
        )
        return list(result.scalars().all())

    # ── Marketplace install (ADR-014 §8.5) ──

    async def install_from_listing(
        self, org_id: str, listing_id: str, user_id: str
    ) -> LearningPath:
        """Cross-org copy of a purchased learning path (R49[36]).

        learning_path is a purchasable product type, but until now nothing
        consumed the license — buyers paid and received a LicenseGrant with no
        way to obtain the content. This is the §8.5 mechanism: license-gated
        fork of the path + items into the buyer org. Copy = fork; later seller
        edits don't sync (v1).
        """
        from app.controlplane import facade as cp_facade
        from app.controlplane.models.marketplace import MarketplaceListing
        from app.models.organization import Organization

        org = await self.db.get(Organization, org_id)
        if org is None:
            raise AppError("ORG_NOT_FOUND", "Organization not found", 404)
        listing = await self.db.get(MarketplaceListing, listing_id)
        if listing is None or listing.product_type != "learning_path":
            raise AppError("LISTING_NOT_FOUND", "Listing not found", 404)

        # The license gate (covering grant / included plan / own product);
        # uniform 404 for private listings, LICENSE_REQUIRED 403 otherwise.
        await cp_facade.check_install_license(self.db, "learning_path", listing.product_id, org)

        source = await self.db.get(LearningPath, listing.product_id)
        if source is None or source.status != ContentStatus.PUBLISHED:
            raise AppError("PATH_NOT_AVAILABLE", "Learning path is not available", 404)

        # Items referencing workflow packs the buyer hasn't installed are a
        # hard 422 listing the gaps — a silently broken curriculum is worse.
        items = await self.list_items(source.id)
        from app.models.skill_pack import InstallStatus
        from app.models.workflow_pack import WorkflowPackInstallation

        needed = {i.workflow_pack_id for i in items if i.workflow_pack_id}
        if needed:
            installed = set(
                (
                    await self.db.execute(
                        select(WorkflowPackInstallation.pack_id).where(
                            WorkflowPackInstallation.org_id == org_id,
                            WorkflowPackInstallation.pack_id.in_(needed),
                            WorkflowPackInstallation.status != InstallStatus.REMOVED,
                        )
                    )
                ).scalars()
            )
            missing = sorted(needed - installed)
            if missing:
                raise AppError(
                    "PATH_DEPENDENCY_MISSING",
                    f"Install these workflow packs first: {', '.join(missing)}",
                    422,
                )

        copy = LearningPath(
            org_id=org_id,
            name=source.name,
            slug=f"{source.slug[:190]}-{secrets.token_hex(3)}",
            description=source.description,
            status=ContentStatus.PUBLISHED,
            estimated_minutes=source.estimated_minutes,
            created_by=user_id,
        )
        self.db.add(copy)
        await self.db.flush()
        for item in items:
            # skill/project refs are org-scoped rows that don't exist in the
            # buyer org — degrade them to informational section headings (ADR)
            # rather than carrying dangling foreign refs.
            if item.item_type in (PathItemType.SKILL, PathItemType.PROJECT):
                self.db.add(
                    LearningPathItem(
                        path_id=copy.id,
                        item_type=PathItemType.SECTION,
                        section_title=(item.section_title or f"[{item.item_type.value}]")[:200],
                        sort_order=item.sort_order,
                        required=False,
                        unlock_rule=item.unlock_rule,
                    )
                )
            else:
                self.db.add(
                    LearningPathItem(
                        path_id=copy.id,
                        item_type=item.item_type,
                        section_title=item.section_title,
                        workflow_pack_id=item.workflow_pack_id,
                        sort_order=item.sort_order,
                        required=item.required,
                        unlock_rule=item.unlock_rule,
                        drip_schedule=item.drip_schedule,
                    )
                )
        await self.db.flush()
        log.info(
            "path_installed_from_listing",
            path_id=copy.id,
            source_path_id=source.id,
            listing_id=listing_id,
            org_id=org_id,
        )
        return copy

    # ── Cohort Assignment ──

    async def _verify_cohort_org(self, cohort_id: str, org_id: str) -> None:
        """Verify the cohort belongs to the same org (prevents cross-tenant IDOR)."""
        from app.models.cohort import Cohort

        cohort = await self.db.get(Cohort, cohort_id)
        if cohort is None or cohort.org_id != org_id:
            raise AppError("COHORT_NOT_FOUND", "Cohort not found in this organization", 404)

    async def assign_to_cohort(
        self, path_id: str, cohort_id: str, org_id: str, assigned_by: str
    ) -> CohortLearningPathAssignment:
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
            # R57[1]: when running inside an outbox-handler SAVEPOINT
            # (worker isolation, provisioning steps), session.rollback()
            # rolls back the ROOT batch transaction — poisoning every
            # sibling message and un-claiming rows mid-flight. Inside a
            # nested transaction we only raise: the enclosing
            # begin_nested() unwinds to the savepoint and the root stays
            # usable. On the plain request path behavior is unchanged.
            if not self.db.in_nested_transaction():
                await self.db.rollback()
            raise AppError(
                "ALREADY_ASSIGNED", "Path already assigned to this cohort", 409
            ) from None
        return assignment

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

    async def list_cohort_paths(
        self, cohort_id: str, org_id: str
    ) -> list[tuple[CohortLearningPathAssignment, str]]:
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

    async def get_path_progress(
        self, path_id: str, user_id: str, org_id: str, cohort_id: str | None = None
    ) -> dict:
        items = await self.list_items(path_id)
        result_items = []
        completed = 0
        total_required = 0
        all_prev_done = True

        # Resolve cohort assignment date for drip schedule gating
        cohort_assigned_at = None
        if cohort_id:
            from app.models.cohort import CohortMember

            member_r = await self.db.execute(
                select(CohortMember.joined_at).where(
                    CohortMember.cohort_id == cohort_id,
                    CohortMember.user_id == user_id,
                )
            )
            cohort_assigned_at = member_r.scalar_one_or_none()

        # Batch-load all referenced skills and projects (avoid N+1)
        skill_ids = [i.skill_id for i in items if i.item_type == PathItemType.SKILL and i.skill_id]
        project_ids = [
            i.project_id for i in items if i.item_type == PathItemType.PROJECT and i.project_id
        ]

        skills_map: dict[str, Skill] = {}
        progress_map: dict[str, SkillProgress] = {}
        projects_map: dict[str, Project] = {}
        approved_projects: set[str] = set()

        if skill_ids:
            s_r = await self.db.execute(select(Skill).where(Skill.id.in_(skill_ids)))
            skills_map = {s.id: s for s in s_r.scalars().all()}
            p_r = await self.db.execute(
                select(SkillProgress).where(
                    SkillProgress.skill_id.in_(skill_ids),
                    SkillProgress.user_id == user_id,
                )
            )
            progress_map = {p.skill_id: p for p in p_r.scalars().all()}

        if project_ids:
            pr_r = await self.db.execute(select(Project).where(Project.id.in_(project_ids)))
            projects_map = {p.id: p for p in pr_r.scalars().all()}
            sub_r = await self.db.execute(
                select(Submission.project_id).where(
                    Submission.project_id.in_(project_ids),
                    Submission.user_id == user_id,
                    Submission.status == SubmissionStatus.APPROVED,
                )
            )
            approved_projects = {row[0] for row in sub_r.all()}

        wf_pack_ids = [
            i.workflow_pack_id
            for i in items
            if i.item_type == PathItemType.WORKFLOW_PACK and i.workflow_pack_id
        ]
        wf_packs_map: dict = {}
        completed_wf_packs: set[str] = set()
        if wf_pack_ids:
            from app.models.workflow_pack import WorkflowPack
            from app.models.workflow_run import RunStatus, WorkflowRun

            wp_r = await self.db.execute(
                select(WorkflowPack).where(WorkflowPack.id.in_(wf_pack_ids))
            )
            wf_packs_map = {p.id: p for p in wp_r.scalars().all()}
            # Done = the learner completed at least one run of the pack in
            # this org (runs reference the pack loosely via pack_id)
            run_r = await self.db.execute(
                select(WorkflowRun.pack_id).where(
                    WorkflowRun.org_id == org_id,
                    WorkflowRun.pack_id.in_(wf_pack_ids),
                    WorkflowRun.started_by == user_id,
                    WorkflowRun.status == RunStatus.COMPLETED,
                )
            )
            completed_wf_packs = {row[0] for row in run_r.all()}

        for item in items:
            if item.item_type == PathItemType.SECTION:
                result_items.append(
                    {
                        "type": "section",
                        "title": item.section_title,
                    }
                )
                continue

            is_required = item.required
            if is_required:
                total_required += 1

            is_done = False
            name = ""

            if item.item_type == PathItemType.SKILL and item.skill_id:
                skill = skills_map.get(item.skill_id)
                name = skill.name if skill else "Unknown"
                progress = progress_map.get(item.skill_id)
                is_done = progress is not None and progress.status == ProgressStatus.COMPLETED

            elif item.item_type == PathItemType.PROJECT and item.project_id:
                project = projects_map.get(item.project_id)
                name = project.title if project else "Unknown"
                is_done = item.project_id in approved_projects

            elif item.item_type == PathItemType.WORKFLOW_PACK and item.workflow_pack_id:
                pack = wf_packs_map.get(item.workflow_pack_id)
                name = pack.name if pack else "Unknown"
                is_done = item.workflow_pack_id in completed_wf_packs

            # Unlock logic
            is_locked = False if item.unlock_rule == "immediate" else not all_prev_done

            # Drip schedule gating
            is_drip_scheduled = False
            if item.drip_schedule and cohort_assigned_at:
                from datetime import UTC, datetime, timedelta

                available_after_days = item.drip_schedule.get("available_after_days", 0)
                drip_available_at = cohort_assigned_at + timedelta(days=available_after_days)
                if datetime.now(UTC) < drip_available_at:
                    is_drip_scheduled = True

            if is_done and is_required:
                completed += 1

            if is_done:
                status = "completed"
            elif is_drip_scheduled:
                status = "scheduled"
            elif is_locked:
                status = "locked"
            else:
                status = "available"

            result_items.append(
                {
                    "type": item.item_type.value,
                    "item_id": item.id,
                    "skill_id": item.skill_id,
                    "project_id": item.project_id,
                    "workflow_pack_id": item.workflow_pack_id,
                    "name": name,
                    "required": is_required,
                    "status": status,
                }
            )

            if is_required:
                all_prev_done = all_prev_done and is_done

        pct = round(completed * 100 / total_required) if total_required > 0 else 0

        # Issue certificate on ACTUAL completion, not the display percentage.
        # R88f: pct is rounded for display — with >=200 required items,
        # 199/200 rounds to 100 and `pct == 100` minted a real certificate
        # (+ path-completion points) with a required item still incomplete.
        certificate_number = None
        if total_required > 0 and completed >= total_required:
            certificate_number, was_new = await self._maybe_issue_certificate(
                path_id, user_id, org_id, completed
            )
            # Award gamification points ONLY when a NEW certificate was just issued
            if was_new and certificate_number is not None:
                try:
                    from app.services.gamification import (
                        POINTS_PATH_COMPLETION,
                        GamificationService,
                    )

                    gam = GamificationService(self.db)
                    await gam.award_points(
                        user_id,
                        org_id,
                        POINTS_PATH_COMPLETION,
                        "path_completion",
                        reference_id=path_id,
                        description=f"Completed learning path {path_id}",
                    )
                except Exception:
                    log.warning(
                        "gamification_award_failed", user_id=user_id, reason="path_completion"
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
    ) -> tuple[str | None, bool]:
        """Issue a completion certificate if one doesn't already exist.

        Returns (certificate_number, was_created). was_created is True only
        when a NEW certificate was just issued (not on subsequent calls).

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
            return existing.certificate_number, False

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
                    skills_data.append(
                        {
                            "skill_id": skill.id,
                            "name": skill.name,
                        }
                    )
            elif item.item_type == PathItemType.PROJECT and item.project_id:
                project = await self.db.get(Project, item.project_id)
                if project:
                    projects_data.append(
                        {
                            "project_id": project.id,
                            "name": project.title,
                        }
                    )

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
        # Use a savepoint so IntegrityError on concurrent insert only rolls
        # back the certificate INSERT, not the entire session transaction.
        try:
            async with self.db.begin_nested():
                self.db.add(cert)
                await self.db.flush()
        except IntegrityError:
            # Concurrent request already created the certificate — re-fetch it
            existing_r2 = await self.db.execute(
                select(Certificate).where(
                    Certificate.user_id == user_id,
                    Certificate.path_id == path_id,
                )
            )
            existing2 = existing_r2.scalar_one_or_none()
            return (existing2.certificate_number if existing2 else None), False

        log.info("certificate_issued", cert_number=cert_number, user_id=user_id, path_id=path_id)
        return cert_number, True

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
            results.append(
                {
                    "user_id": member.user_id,
                    "completed": progress["completed"],
                    "total_required": progress["total_required"],
                    "pct": progress["pct"],
                }
            )

        return results

    # ── Helpers ──

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]

"""Skill Pack management service — CRUD, contents, publish releases."""

import hashlib
import json
import re
import secrets
from collections import defaultdict, deque
from datetime import date, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.project import ProjectTemplate
from app.models.skill import (
    ContentStatus,
    Exercise,
    Skill,
    SkillCategory,
    SkillPrerequisite,
)
from app.models.skill_pack import (
    InstallStatus,
    PackStatus,
    PackVisibility,
    SkillPack,
    SkillPackInstallation,
    SkillPackRelease,
    SkillPackSkill,
    SkillPackTemplate,
)

log = structlog.get_logger()

MAX_SKILLS_PER_PACK = 200
MAX_TEMPLATES_PER_PACK = 50
MAX_MANIFEST_BYTES = 10_000_000  # 10 MB


def _parse_semver(version: str) -> tuple[int, int, int, str]:
    """Parse 'X.Y.Z' or 'X.Y.Z-prerelease' into a comparable tuple.

    Pre-release versions sort BEFORE the release (1.0.0-alpha < 1.0.0)
    by using the pre-release string directly. An empty string sorts
    after any pre-release label because '' > any non-empty string is
    False — so we use a high-sorting sentinel for the release.
    """
    base, _, prerelease = version.partition("-")
    parts = base.split(".")
    # Sentinel: release (no prerelease) sorts AFTER all pre-release strings
    pre_key = prerelease if prerelease else "~"  # '~' > all ASCII letters
    return (int(parts[0]), int(parts[1]), int(parts[2]), pre_key)


# ── Errors ────────────────────────────────────────────────


class PackNotFoundError(AppError):
    def __init__(self):
        super().__init__("PACK_NOT_FOUND", "Skill pack not found", 404)


class ReleaseNotFoundError(AppError):
    def __init__(self):
        super().__init__("RELEASE_NOT_FOUND", "Release not found", 404)


# ── Service ──────────────────────────────────────────────


class SkillPackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Pack CRUD ──

    async def create_pack(
        self,
        org_id: str,
        created_by: str,
        **fields,
    ) -> SkillPack:
        # Approval gate at CREATE, completing R60's class (which gated PUT only,
        # update_pack below). A newly-created pack can never be pre-approved
        # (review_status starts None), and the anon registry serves
        # review_status IS NULL as grandfathered-approved (registry.py), so a
        # direct POST visibility=public + publish listed an unapproved pack in
        # the public registry — the identical bypass R60 closed for update.
        # PUBLIC is reachable only via submit-review → approve. The workflow
        # twin is already safe (CreateWorkflowPackRequest has no visibility
        # field); this brings skill-pack create to parity.
        requested_visibility = fields.get("visibility")
        if requested_visibility in ("public", PackVisibility.PUBLIC):
            raise AppError(
                "APPROVAL_REQUIRED",
                "Public visibility requires approval — create the pack, then submit for review",
                422,
            )
        name = fields.get("name", "Untitled Pack")
        slug = self._generate_slug(name)

        pack = SkillPack(
            owner_org_id=org_id,
            slug=slug,
            created_by=created_by,
            **fields,
        )
        # Always add random suffix to slug to avoid IntegrityError + rollback issues
        pack.slug = f"{slug[:190]}-{secrets.token_hex(3)}"
        self.db.add(pack)
        await self.db.flush()

        log.info("pack_created", pack_id=pack.id, org_id=org_id)
        return pack

    async def list_packs(
        self,
        org_id: str,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[SkillPack], int]:
        base = select(SkillPack).where(SkillPack.owner_org_id == org_id)
        if status:
            try:
                parsed_status = PackStatus(status)
            except ValueError:
                raise AppError("INVALID_STATUS", f"Unknown status '{status}'", 422) from None
            base = base.where(SkillPack.status == parsed_status)
        else:
            base = base.where(SkillPack.status != PackStatus.ARCHIVED)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(SkillPack.created_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_pack(self, pack_id: str, org_id: str, for_update: bool = False) -> SkillPack:
        # for_update: row-lock + refresh to committed state (populate_existing)
        # for mutators. Same stale-read-write class as the workflow-pack family
        # (R70b): every mutation here was a db.get snapshot + unguarded ORM
        # setattr under READ COMMITTED — reproduced the identical approval
        # BYPASS (update_pack(visibility=public) passing its stale 'approved'
        # gate while a concurrent card-change had already voided approval,
        # publishing an unapproved pack to the registry). The lock serializes
        # the writers; the loser re-reads fresh so its own gate fires.
        if for_update:
            result = await self.db.execute(
                select(SkillPack)
                .where(SkillPack.id == pack_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            pack = result.scalar_one_or_none()
        else:
            pack = await self.db.get(SkillPack, pack_id)
        if pack is None or pack.owner_org_id != org_id:
            raise PackNotFoundError()
        if pack.status == PackStatus.ARCHIVED:
            raise PackNotFoundError()
        return pack

    async def update_pack(self, pack_id: str, org_id: str, **fields) -> SkillPack:
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        # Approval gate (mirror of WorkflowPackService.update_pack): PUBLIC
        # visibility is only reachable via submit-review → approve. A direct
        # PUT visibility=public on an unapproved pack would list it in the
        # registry (which serves review_status IS NULL OR approved),
        # bypassing review entirely.
        requested_visibility = fields.get("visibility")
        if (
            requested_visibility in ("public", PackVisibility.PUBLIC)
            and pack.review_status != "approved"
        ):
            raise AppError(
                "APPROVAL_REQUIRED",
                "Public visibility requires approval — submit for review first",
                422,
            )
        if fields.get("name"):
            slug = self._generate_slug(fields["name"])
            pack.slug = f"{slug[:190]}-{secrets.token_hex(3)}"
        # Card fields drive the public registry card — editing any on an
        # APPROVED pack voids approval (else innocuous-approve then swap the
        # public card past the gate), same as WorkflowPackService.
        # MUST cover every field PublicSkillPackResponse serializes to the anon
        # registry (R82): a hand-picked subset let estimated_minutes / language
        # / learning_outcomes / provenance be swapped past the gate — all shown
        # on the public card, all editable via UpdateSkillPackRequest, none
        # previously void-triggering. Keep in sync with PublicSkillPackResponse.
        _card_fields = (
            "name",
            "summary",
            "description",
            "scenario_tags",
            "tool_tags",
            "capability_tags",
            "difficulty",
            "cover_image_key",
            "estimated_minutes",
            "language",
            "learning_outcomes",
            "provenance",
        )
        card_changed = any(
            key in _card_fields and value is not None and getattr(pack, key, None) != value
            for key, value in fields.items()
        )
        for k, v in fields.items():
            if v is not None and hasattr(pack, k):
                setattr(pack, k, v)
        # Void on approved OR pending (R84): a card edit while the pack is
        # under review ('pending') would otherwise leave the reviewer approving
        # stale content the author swapped after submitting — reset to draft so
        # the swapped card must be re-submitted. (Public→unlisted only matters
        # for the approved case; a pending pack is not yet public.)
        if card_changed and pack.review_status in ("approved", "pending"):
            pack.review_status = None
            if pack.visibility == PackVisibility.PUBLIC:
                pack.visibility = PackVisibility.UNLISTED
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError("SLUG_CONFLICT", "A pack with this name already exists", 409) from None
        await self.db.refresh(pack)
        from app.core.cache import cache_delete_pattern

        await cache_delete_pattern("registry:*")
        return pack

    async def delete_pack(self, pack_id: str, org_id: str) -> None:
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        pack.status = PackStatus.ARCHIVED

        # Clean up join-table references
        from sqlalchemy import delete as sa_delete

        from app.models.pack_share import PackShare

        await self.db.execute(sa_delete(SkillPackSkill).where(SkillPackSkill.pack_id == pack_id))
        await self.db.execute(
            sa_delete(SkillPackTemplate).where(SkillPackTemplate.pack_id == pack_id)
        )
        await self.db.execute(sa_delete(PackShare).where(PackShare.pack_id == pack_id))

        await self.db.flush()
        from app.core.cache import cache_delete_pattern

        await cache_delete_pattern("registry:*")

    # ── Pack Contents ──

    async def add_skill(
        self, pack_id: str, skill_id: str, org_id: str, sort_order: int = 0
    ) -> None:
        await self.get_pack(pack_id, org_id)  # validates existence + ownership

        # Enforce skill count limit before insert
        count_r = await self.db.execute(
            select(func.count()).where(SkillPackSkill.pack_id == pack_id)
        )
        if count_r.scalar_one() >= MAX_SKILLS_PER_PACK:
            raise AppError("PACK_TOO_LARGE", f"Maximum {MAX_SKILLS_PER_PACK} skills per pack", 422)

        skill = await self.db.get(Skill, skill_id)
        if skill is None or skill.org_id != org_id:
            raise AppError("SKILL_NOT_FOUND", "Skill not found in this organization", 404)

        entry = SkillPackSkill(pack_id=pack_id, skill_id=skill_id, sort_order=sort_order)
        self.db.add(entry)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError("SKILL_ALREADY_IN_PACK", "Skill already in this pack", 409) from None

    async def remove_skill(self, pack_id: str, skill_id: str, org_id: str) -> None:
        await self.get_pack(pack_id, org_id)
        result = await self.db.execute(
            select(SkillPackSkill).where(
                SkillPackSkill.pack_id == pack_id,
                SkillPackSkill.skill_id == skill_id,
            )
        )
        entry = result.scalar_one_or_none()
        if entry is None:
            raise AppError("NOT_IN_PACK", "Skill not in this pack", 404)
        await self.db.delete(entry)
        await self.db.flush()

    async def list_pack_skills(self, pack_id: str) -> list[tuple[SkillPackSkill, str]]:
        result = await self.db.execute(
            select(SkillPackSkill, Skill.name)
            .join(Skill, Skill.id == SkillPackSkill.skill_id)
            .where(
                SkillPackSkill.pack_id == pack_id,
                Skill.status != ContentStatus.ARCHIVED,
            )
            .order_by(SkillPackSkill.sort_order)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def add_template(
        self, pack_id: str, template_id: str, org_id: str, sort_order: int = 0
    ) -> None:
        await self.get_pack(pack_id, org_id)  # validates existence + ownership

        tmpl = await self.db.get(ProjectTemplate, template_id)
        if tmpl is None or tmpl.org_id != org_id:
            raise AppError("TEMPLATE_NOT_FOUND", "Template not found in this organization", 404)

        entry = SkillPackTemplate(pack_id=pack_id, template_id=template_id, sort_order=sort_order)
        self.db.add(entry)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError(
                "TEMPLATE_ALREADY_IN_PACK", "Template already in this pack", 409
            ) from None

    async def remove_template(self, pack_id: str, template_id: str, org_id: str) -> None:
        await self.get_pack(pack_id, org_id)
        result = await self.db.execute(
            select(SkillPackTemplate).where(
                SkillPackTemplate.pack_id == pack_id,
                SkillPackTemplate.template_id == template_id,
            )
        )
        entry = result.scalar_one_or_none()
        if entry is None:
            raise AppError("NOT_IN_PACK", "Template not in this pack", 404)
        await self.db.delete(entry)
        await self.db.flush()

    async def list_pack_templates(self, pack_id: str) -> list[tuple[SkillPackTemplate, str]]:
        result = await self.db.execute(
            select(SkillPackTemplate, ProjectTemplate.name)
            .join(ProjectTemplate, ProjectTemplate.id == SkillPackTemplate.template_id)
            .where(
                SkillPackTemplate.pack_id == pack_id,
                ProjectTemplate.status != ContentStatus.ARCHIVED,
            )
            .order_by(SkillPackTemplate.sort_order)
        )
        return [(row[0], row[1]) for row in result.all()]

    # ── Approval Workflow ──

    async def approve_pack(self, pack_id: str, org_id: str, actor_id: str) -> SkillPack:
        """Approve a pack for public visibility."""
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        if pack.review_status != "pending":
            raise AppError("NOT_PENDING", "Pack is not pending review", 422)
        pack.review_status = "approved"
        pack.visibility = PackVisibility.PUBLIC
        pack.rejection_reason = None  # R84: clear a stale prior-rejection note
        await self.db.flush()
        await self.db.refresh(pack)

        await self._record_approval_event(pack_id, "approved", actor_id)
        from app.core.cache import cache_delete_pattern

        await cache_delete_pattern("registry:*")
        log.info("pack_approved", pack_id=pack_id, org_id=org_id)
        return pack

    async def reject_pack(
        self, pack_id: str, org_id: str, reason: str | None = None, actor_id: str | None = None
    ) -> SkillPack:
        """Reject a pack from public visibility."""
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        if pack.review_status != "pending":
            raise AppError("NOT_PENDING", "Pack is not pending review", 422)
        pack.review_status = "rejected"
        pack.rejection_reason = reason
        await self.db.flush()
        await self.db.refresh(pack)

        if actor_id:
            await self._record_approval_event(pack_id, "rejected", actor_id, reason)
        from app.core.cache import cache_delete_pattern

        await cache_delete_pattern("registry:*")
        log.info("pack_rejected", pack_id=pack_id, org_id=org_id, reason=reason)
        return pack

    async def submit_for_review(self, pack_id: str, org_id: str, actor_id: str) -> SkillPack:
        """Submit a pack for approval review."""
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        if pack.review_status == "pending":
            raise AppError("ALREADY_PENDING", "Pack is already pending review", 409)
        if pack.review_status == "approved":
            raise AppError("ALREADY_APPROVED", "Cannot re-submit an approved pack", 422)
        pack.review_status = "pending"
        await self.db.flush()
        await self.db.refresh(pack)

        await self._record_approval_event(pack_id, "submitted", actor_id)
        log.info("pack_submitted_for_review", pack_id=pack_id, org_id=org_id)
        return pack

    async def _record_approval_event(
        self,
        pack_id: str,
        action: str,
        actor_id: str,
        reason: str | None = None,
    ) -> None:
        from app.models.notification import PackApprovalEvent

        event = PackApprovalEvent(
            pack_id=pack_id,
            action=action,
            actor_id=actor_id,
            reason=reason,
        )
        self.db.add(event)
        await self.db.flush()

    async def list_approval_history(self, pack_id: str, org_id: str) -> list:
        """Return chronological approval audit trail for a pack."""
        from app.models.notification import PackApprovalEvent

        await self.get_pack(pack_id, org_id)  # validates existence + ownership
        result = await self.db.execute(
            select(PackApprovalEvent)
            .where(PackApprovalEvent.pack_id == pack_id)
            .order_by(PackApprovalEvent.created_at.desc())
        )
        return list(result.scalars().all())

    # ── Releases ──

    async def publish_release(
        self,
        pack_id: str,
        org_id: str,
        version: str,
        changelog: str | None,
        released_by: str,
    ) -> SkillPackRelease:
        pack = await self.get_pack(pack_id, org_id, for_update=True)

        # Validate semver
        if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$", version):
            raise AppError("INVALID_VERSION", "Version must be semver format (e.g. 1.0.0)", 422)

        # Check duplicate version
        dup = await self.db.execute(
            select(SkillPackRelease.id).where(
                SkillPackRelease.pack_id == pack_id,
                SkillPackRelease.version == version,
            )
        )
        if dup.scalar_one_or_none():
            raise AppError("DUPLICATE_VERSION", f"Version {version} already exists", 409)

        # Load pack skills
        skill_rows = await self.db.execute(
            select(SkillPackSkill.skill_id, SkillPackSkill.sort_order)
            .where(SkillPackSkill.pack_id == pack_id)
            .order_by(SkillPackSkill.sort_order)
        )
        skill_entries = skill_rows.all()

        # Load pack templates
        tmpl_rows = await self.db.execute(
            select(SkillPackTemplate.template_id, SkillPackTemplate.sort_order)
            .where(SkillPackTemplate.pack_id == pack_id)
            .order_by(SkillPackTemplate.sort_order)
        )
        tmpl_entries = tmpl_rows.all()

        if not skill_entries and not tmpl_entries:
            raise AppError("EMPTY_PACK", "Pack must contain at least one skill or template", 422)
        if len(skill_entries) > MAX_SKILLS_PER_PACK:
            raise AppError("PACK_TOO_LARGE", f"Max {MAX_SKILLS_PER_PACK} skills per pack", 422)
        if len(tmpl_entries) > MAX_TEMPLATES_PER_PACK:
            raise AppError(
                "PACK_TOO_LARGE", f"Max {MAX_TEMPLATES_PER_PACK} templates per pack", 422
            )

        # Build manifest
        skill_ids = [sid for sid, _ in skill_entries]
        categories_map: dict[str, dict] = {}
        skills_manifest: list[dict] = []

        # Load prerequisite edges (for intra-pack cycle detection)
        prereq_r = await self.db.execute(
            select(SkillPrerequisite).where(SkillPrerequisite.skill_id.in_(skill_ids))
        )
        all_prereqs = [(p.skill_id, p.prerequisite_id) for p in prereq_r.scalars().all()]
        pack_skill_set = set(skill_ids)
        intra_prereqs = [(s, p) for s, p in all_prereqs if p in pack_skill_set]

        if self._has_cycle(intra_prereqs, pack_skill_set):
            raise AppError("PREREQUISITE_CYCLE", "Prerequisite graph contains a cycle", 422)

        # Batch load all skills
        skills_r = await self.db.execute(select(Skill).where(Skill.id.in_(skill_ids)))
        skills_by_id = {s.id: s for s in skills_r.scalars().all()}

        # Batch load categories
        cat_ids = {s.category_id for s in skills_by_id.values() if s.category_id}
        if cat_ids:
            cats_r = await self.db.execute(
                select(SkillCategory).where(SkillCategory.id.in_(cat_ids))
            )
            cats_by_id: dict[str, SkillCategory] = {c.id: c for c in cats_r.scalars().all()}
        else:
            cats_by_id = {}

        # Batch load exercises grouped by skill
        exercises_r = await self.db.execute(
            select(Exercise)
            .where(Exercise.skill_id.in_(skill_ids), Exercise.status != ContentStatus.ARCHIVED)
            .order_by(Exercise.sort_order)
        )
        exercises_by_skill: dict[str, list] = defaultdict(list)
        for ex in exercises_r.scalars().all():
            exercises_by_skill[ex.skill_id].append(ex)

        # Batch load templates
        tmpl_ids = [tid for tid, _ in tmpl_entries]
        if tmpl_ids:
            tmpls_r = await self.db.execute(
                select(ProjectTemplate).where(ProjectTemplate.id.in_(tmpl_ids))
            )
            tmpls_by_id: dict[str, ProjectTemplate] = {t.id: t for t in tmpls_r.scalars().all()}
        else:
            tmpls_by_id = {}

        for sid, sort in skill_entries:
            skill = skills_by_id.get(sid)
            if skill is None or skill.status == ContentStatus.ARCHIVED:
                raise AppError("COMPONENT_ARCHIVED", f"Skill '{sid}' is archived or missing", 422)

            exercises = exercises_by_skill.get(sid, [])

            # Category
            category = cats_by_id.get(skill.category_id) if skill.category_id else None
            if category and category.slug not in categories_map:
                categories_map[category.slug] = {
                    "logical_id": category.slug,
                    "name": category.name,
                    "slug": category.slug,
                    "sort_order": category.sort_order,
                }

            # Prerequisite logical_ids
            skill_prereq_slugs = []
            for s_id, p_id in all_prereqs:
                if s_id == skill.id and p_id in pack_skill_set:
                    prereq_skill = skills_by_id.get(p_id)
                    if prereq_skill:
                        skill_prereq_slugs.append(prereq_skill.slug)

            skills_manifest.append(
                {
                    "logical_id": skill.slug,
                    "category_logical_id": category.slug if category else None,
                    "name": skill.name,
                    "slug": skill.slug,
                    "description": skill.description,
                    "learning_content": skill.learning_content,
                    "difficulty": skill.difficulty.value if skill.difficulty else None,
                    "estimated_minutes": skill.estimated_minutes,
                    "tags": skill.tags or [],
                    "sort_order": sort,
                    "exercises": [
                        {
                            "logical_id": f"{skill.slug}/{ex.title.lower().replace(' ', '-')[:50]}",
                            "title": ex.title,
                            "description": ex.description,
                            "type": ex.type.value,
                            "config": ex.config,
                            "max_score": ex.max_score,
                            "sort_order": ex.sort_order,
                        }
                        for ex in exercises
                    ],
                    "prerequisites": skill_prereq_slugs,
                }
            )

        templates_manifest: list[dict] = []
        for tid, sort in tmpl_entries:
            tmpl = tmpls_by_id.get(tid)
            if tmpl is None or tmpl.status == ContentStatus.ARCHIVED:
                raise AppError(
                    "COMPONENT_ARCHIVED", f"Template '{tid}' is archived or missing", 422
                )
            templates_manifest.append(
                {
                    "logical_id": re.sub(r"[^a-z0-9]+", "-", tmpl.name.lower()).strip("-")[:100],
                    "name": tmpl.name,
                    "description": tmpl.description,
                    "instructions": tmpl.instructions,
                    "project_type": tmpl.project_type,
                    "difficulty": tmpl.difficulty.value if tmpl.difficulty else "intermediate",
                    "suggested_minutes": tmpl.suggested_minutes,
                    "max_score": tmpl.max_score,
                    "rubric": tmpl.rubric,
                    "deliverables": tmpl.deliverables or [],
                    "skill_names": tmpl.skill_names or [],
                    "sort_order": sort,
                }
            )

        # Validate logical_id uniqueness across all components
        all_logical_ids: list[str] = []
        for s in skills_manifest:
            all_logical_ids.append(s["logical_id"])
            for ex in s.get("exercises", []):
                all_logical_ids.append(ex["logical_id"])
        for t in templates_manifest:
            all_logical_ids.append(t["logical_id"])

        seen_ids: set[str] = set()
        for lid in all_logical_ids:
            if lid in seen_ids:
                # Provide a hint about the collision source
                hint = ""
                if "/" in lid:
                    # Exercise logical_ids have the form "skill-slug/exercise-slug"
                    hint = (
                        " This is likely caused by two exercises with titles "
                        "that normalize to the same slug within the same skill."
                    )
                raise AppError(
                    "DUPLICATE_LOGICAL_ID",
                    f"Duplicate logical_id '{lid}' — rename components to have distinct slugs.{hint}",
                    422,
                )
            seen_ids.add(lid)

        manifest = {
            "schema_version": "1",
            "version": version,
            "pack": {
                "name": pack.name,
                "summary": pack.summary,
                "metadata": {
                    "difficulty": pack.difficulty,
                    "estimated_minutes": pack.estimated_minutes,
                    "scenario_tags": pack.scenario_tags or [],
                    "tool_tags": pack.tool_tags or [],
                    "capability_tags": pack.capability_tags or [],
                    "learning_outcomes": pack.learning_outcomes or [],
                    "language": pack.language,
                },
                "provenance": pack.provenance or {},
            },
            "categories": list(categories_map.values()),
            "skills": skills_manifest,
            "project_templates": templates_manifest,
        }

        canonical = json.dumps(manifest, sort_keys=True, ensure_ascii=True)
        if len(canonical) > MAX_MANIFEST_BYTES:
            raise AppError(
                "MANIFEST_TOO_LARGE",
                f"Manifest exceeds {MAX_MANIFEST_BYTES // 1_000_000}MB limit",
                422,
            )

        checksum = hashlib.sha256(canonical.encode()).hexdigest()

        release = SkillPackRelease(
            pack_id=pack_id,
            version=version,
            manifest=manifest,
            changelog=changelog,
            checksum=checksum,
            component_count=len(skills_manifest) + len(templates_manifest),
            released_by=released_by,
        )
        self.db.add(release)

        # Promote to published on first release
        if pack.status == PackStatus.DRAFT:
            pack.status = PackStatus.PUBLISHED

        # Publishing a NEW release on an already-approved OR pending pack
        # changes the content the anon registry serves / the reviewer is
        # examining — the preview/curriculum reads the LATEST release manifest
        # (registry.get_pack_preview). Void approval (R83) and also reset a
        # pending review (R84) so a post-submit release can't be approved as if
        # it were the reviewed content.
        if pack.review_status in ("approved", "pending"):
            pack.review_status = None
            if pack.visibility == PackVisibility.PUBLIC:
                pack.visibility = PackVisibility.UNLISTED

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError("DUPLICATE_VERSION", f"Version {version} already exists", 409) from None

        # Invalidate registry cache after new release
        from app.core.cache import cache_delete_pattern

        await cache_delete_pattern("registry:*")

        # Recompute and persist badges for this pack
        from app.services.registry import RegistryService as _RegSvc

        await _RegSvc(self.db).recompute_pack_badges(pack_id)

        # Notify installing orgs' owners about the new version
        try:
            from app.models.organization import MemberStatus, OrgMember, OrgRole
            from app.services.notification import NotificationService

            install_r = await self.db.execute(
                select(SkillPackInstallation.org_id).where(
                    SkillPackInstallation.pack_id == pack_id,
                    SkillPackInstallation.status == InstallStatus.ACTIVE,
                )
            )
            org_ids = [row[0] for row in install_r.all()]
            if org_ids:
                owner_r = await self.db.execute(
                    select(OrgMember.user_id, OrgMember.org_id).where(
                        OrgMember.org_id.in_(org_ids),
                        OrgMember.role == OrgRole.OWNER,
                        OrgMember.status == MemberStatus.ACTIVE,
                    )
                )
                notif_svc = NotificationService(self.db)
                for user_id, org_id_val in owner_r.all():
                    try:
                        await notif_svc.create(
                            user_id=user_id,
                            notification_type="pack.updated",
                            title=f"New version {version} available for {pack.name}",
                            body=changelog[:500] if changelog else None,
                            org_id=org_id_val,
                            data={"pack_id": pack_id, "version": version},
                        )
                    except Exception:
                        log.warning(
                            "notify_pack_update_failed_user",
                            pack_id=pack_id,
                            user_id=user_id,
                            version=version,
                        )
        except Exception:
            log.warning("notify_pack_update_failed", pack_id=pack_id, version=version)

        # Compute and persist quality score
        try:
            from app.services.registry import RegistryService as _RegSvc2

            reg_svc = _RegSvc2(self.db)
            pack.quality_score = await reg_svc.compute_quality_score(pack)
            await self.db.flush()
        except Exception:
            log.warning("quality_score_failed", pack_id=pack_id)

        # Fire webhook event
        try:
            from app.services.webhook import WebhookService

            webhook_svc = WebhookService(self.db)
            await webhook_svc.trigger_event(
                pack.owner_org_id,
                "pack.published",
                {"pack_id": pack_id, "version": version, "name": pack.name},
            )
        except Exception as exc:
            log.warning(
                "webhook_trigger_failed",
                pack_id=pack_id,
                webhook_event="pack.published",
                error=str(exc),
            )

        log.info(
            "pack_released",
            pack_id=pack_id,
            version=version,
            components=release.component_count,
            checksum=checksum,
        )
        return release

    async def list_releases(self, pack_id: str) -> list[SkillPackRelease]:
        from sqlalchemy.orm import defer

        result = await self.db.execute(
            select(SkillPackRelease)
            .where(SkillPackRelease.pack_id == pack_id)
            .options(defer(SkillPackRelease.manifest))
        )
        releases = list(result.scalars().all())
        releases.sort(key=lambda r: _parse_semver(r.version), reverse=True)
        return releases

    async def get_release(self, pack_id: str, version: str) -> SkillPackRelease:
        result = await self.db.execute(
            select(SkillPackRelease).where(
                SkillPackRelease.pack_id == pack_id,
                SkillPackRelease.version == version,
            )
        )
        release = result.scalar_one_or_none()
        if release is None:
            raise ReleaseNotFoundError()
        return release

    # ── Analytics ──

    async def get_pack_analytics(self, pack_id: str, org_id: str) -> dict:
        """Publisher analytics for a pack: installs, rating, installs by version, installs by day."""
        pack = await self.get_pack(pack_id, org_id)

        # Installs grouped by installed_version
        version_r = await self.db.execute(
            select(
                SkillPackInstallation.installed_version,
                func.count().label("count"),
            )
            .where(
                SkillPackInstallation.pack_id == pack_id,
                SkillPackInstallation.status != InstallStatus.REMOVED,
            )
            .group_by(SkillPackInstallation.installed_version)
        )
        installs_by_version = [{"version": row[0], "count": row[1]} for row in version_r.all()]

        # Installs by day for the last 30 days
        today = date.today()
        thirty_days_ago = today - timedelta(days=29)

        day_r = await self.db.execute(
            select(
                func.date(SkillPackInstallation.installed_at).label("day"),
                func.count().label("count"),
            )
            .where(
                SkillPackInstallation.pack_id == pack_id,
                SkillPackInstallation.installed_at >= thirty_days_ago,
            )
            .group_by(func.date(SkillPackInstallation.installed_at))
            .order_by(func.date(SkillPackInstallation.installed_at))
        )
        db_days: dict[date, int] = {row[0]: row[1] for row in day_r.all()}

        # Fill missing days with 0
        installs_by_day: list[dict] = []
        for offset in range(30):
            day = thirty_days_ago + timedelta(days=offset)
            installs_by_day.append(
                {
                    "date": day.isoformat(),
                    "count": db_days.get(day, 0),
                }
            )

        return {
            "install_count": pack.install_count,
            "average_rating": pack.average_rating,
            "review_count": pack.review_count,
            "installs_by_version": installs_by_version,
            "installs_by_day": installs_by_day,
        }

    # ── Helpers ──

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]

    @staticmethod
    def _has_cycle(edges: list[tuple[str, str]], nodes: set[str]) -> bool:
        """Kahn's algorithm — returns True if directed graph has a cycle."""
        adj: dict[str, set[str]] = defaultdict(set)
        in_degree: dict[str, int] = {n: 0 for n in nodes}
        for src, dst in edges:
            adj[dst].add(src)
            in_degree[src] = in_degree.get(src, 0) + 1
        queue = deque(n for n in nodes if in_degree.get(n, 0) == 0)
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return visited != len(nodes)

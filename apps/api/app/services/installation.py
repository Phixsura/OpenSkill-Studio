"""Pack installation, upgrade, diff, and fork service."""

import re
import secrets

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.project import ProjectTemplate
from app.models.skill import (
    ContentStatus,
    Exercise,
    ExerciseType,
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
)

log = structlog.get_logger()


def _parse_semver(version: str) -> tuple[int, int, int, str]:
    """Parse 'X.Y.Z' or 'X.Y.Z-prerelease' into a comparable tuple.

    Pre-release versions sort BEFORE the release (1.0.0-alpha < 1.0.0).
    """
    base, _, prerelease = version.partition("-")
    parts = base.split(".")
    pre_key = prerelease if prerelease else "~"  # '~' > all ASCII letters
    return (int(parts[0]), int(parts[1]), int(parts[2]), pre_key)


# ── Errors ────────────────────────────────────────────────


class InstallationNotFoundError(AppError):
    def __init__(self):
        super().__init__("INSTALLATION_NOT_FOUND", "Installation not found", 404)


# ── Service ──────────────────────────────────────────────


class InstallationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Install ──

    async def install_pack(
        self,
        org_id: str,
        pack_id: str,
        version: str | None,
        installed_by: str,
    ) -> SkillPackInstallation:
        """Install a specific pack release into an organization."""
        pack = await self.db.get(SkillPack, pack_id)
        if pack is None:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)

        # Status check: only PUBLISHED packs can be installed.
        # Use PACK_NOT_FOUND (not PACK_NOT_AVAILABLE) to prevent information
        # disclosure — different error codes would let attackers enumerate
        # which pack IDs exist in draft/archived state across organizations.
        if pack.status != PackStatus.PUBLISHED:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)

        # Visibility check
        if pack.visibility == PackVisibility.PRIVATE and pack.owner_org_id != org_id:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)

        # Get release (latest if no version specified)
        if version:
            release_r = await self.db.execute(
                select(SkillPackRelease).where(
                    SkillPackRelease.pack_id == pack_id,
                    SkillPackRelease.version == version,
                )
            )
            release = release_r.scalar_one_or_none()
        else:
            release_r = await self.db.execute(
                select(SkillPackRelease).where(SkillPackRelease.pack_id == pack_id)
            )
            all_releases = list(release_r.scalars().all())
            release = max(all_releases, key=lambda r: _parse_semver(r.version)) if all_releases else None

        if release is None:
            raise AppError("RELEASE_NOT_FOUND", "No release found for this pack", 404)

        # Check not already installed
        existing = await self.db.execute(
            select(SkillPackInstallation).where(
                SkillPackInstallation.org_id == org_id,
                SkillPackInstallation.pack_id == pack_id,
                SkillPackInstallation.status != InstallStatus.REMOVED,
            )
        )
        existing_install = existing.scalar_one_or_none()
        if existing_install:
            raise AppError("ALREADY_INSTALLED", "Pack already installed in this organization", 409)

        # Remove any old REMOVED installation row to avoid unique constraint violation
        old_removed_r = await self.db.execute(
            select(SkillPackInstallation).where(
                SkillPackInstallation.org_id == org_id,
                SkillPackInstallation.pack_id == pack_id,
                SkillPackInstallation.status == InstallStatus.REMOVED,
            )
        )
        old_removed = old_removed_r.scalar_one_or_none()
        if old_removed:
            await self.db.delete(old_removed)
            await self.db.flush()

        manifest = release.manifest
        release_id = release.id
        release_version = release.version

        # Create categories
        cat_id_map: dict[str, str] = {}  # logical_id -> new ULID
        for cat_def in manifest.get("categories", []):
            cat = SkillCategory(
                org_id=org_id,
                name=cat_def["name"],
                slug=cat_def["slug"],
                sort_order=cat_def.get("sort_order", 0),
                status=ContentStatus.PUBLISHED,
                origin_pack_id=pack_id,
                origin_release_id=release_id,
                origin_component_id=cat_def["logical_id"],
                created_by=installed_by,
            )
            # Always add random suffix to prevent slug conflicts with existing org content
            import secrets as _cat_secrets
            cat.slug = f"{cat.slug[:90]}-{_cat_secrets.token_hex(3)}"
            self.db.add(cat)
            await self.db.flush()
            cat_id_map[cat_def["logical_id"]] = cat.id

        # Create skills + exercises
        skill_id_map: dict[str, str] = {}  # logical_id -> new ULID
        for skill_def in manifest.get("skills", []):
            cat_logical = skill_def.get("category_logical_id")
            category_id = cat_id_map.get(cat_logical) if cat_logical else None

            if category_id is None and cat_logical:
                raise AppError(
                    "CATEGORY_NOT_FOUND",
                    f"Category '{cat_logical}' referenced by skill '{skill_def['name']}' not found in manifest",
                    422,
                )

            import secrets as _secrets

            skill = Skill(
                org_id=org_id,
                category_id=category_id,
                name=skill_def["name"],
                slug=re.sub(r"[^a-z0-9]+", "-", skill_def.get("slug", skill_def["name"]).lower()).strip("-")[:200] or f"skill-{secrets.token_hex(3)}",
                description=skill_def.get("description", ""),
                learning_content=skill_def.get("learning_content"),
                difficulty=skill_def.get("difficulty", "beginner"),
                estimated_minutes=skill_def.get("estimated_minutes"),
                tags=skill_def.get("tags", []),
                sort_order=skill_def.get("sort_order", 0),
                status=ContentStatus.PUBLISHED,
                origin_pack_id=pack_id,
                origin_release_id=release_id,
                origin_component_id=skill_def["logical_id"],
                created_by=installed_by,
            )
            # Always add random suffix to prevent slug conflicts with existing org content
            skill.slug = f"{skill.slug[:190]}-{_secrets.token_hex(3)}"
            self.db.add(skill)
            await self.db.flush()
            skill_id_map[skill_def["logical_id"]] = skill.id

            # Create exercises
            for ex_def in skill_def.get("exercises", []):
                exercise = Exercise(
                    org_id=org_id,
                    skill_id=skill.id,
                    title=ex_def["title"],
                    description=ex_def.get("description", ""),
                    type=ExerciseType(ex_def.get("type", "text_answer")),
                    config=ex_def.get("config", {}),
                    max_score=ex_def.get("max_score", 100),
                    sort_order=ex_def.get("sort_order", 0),
                    status=ContentStatus.PUBLISHED,
                    origin_pack_id=pack_id,
                    origin_release_id=release_id,
                    origin_component_id=ex_def.get("logical_id", ""),
                    created_by=installed_by,
                )
                self.db.add(exercise)

        await self.db.flush()

        # Create prerequisites (resolve logical_id -> new skill_id)
        for skill_def in manifest.get("skills", []):
            for prereq_logical in skill_def.get("prerequisites", []):
                if prereq_logical in skill_id_map and skill_def["logical_id"] in skill_id_map:
                    prereq = SkillPrerequisite(
                        skill_id=skill_id_map[skill_def["logical_id"]],
                        prerequisite_id=skill_id_map[prereq_logical],
                    )
                    self.db.add(prereq)

        # Create project templates
        for tmpl_def in manifest.get("project_templates", []):
            tmpl = ProjectTemplate(
                org_id=org_id,
                name=tmpl_def["name"],
                description=tmpl_def.get("description", ""),
                instructions=tmpl_def.get("instructions", ""),
                project_type=tmpl_def.get("project_type", "general"),
                difficulty=tmpl_def.get("difficulty", "intermediate"),
                suggested_minutes=tmpl_def.get("suggested_minutes"),
                max_score=tmpl_def.get("max_score", 100),
                rubric=tmpl_def.get("rubric", [{"criterion": "Overall", "max_score": 100}]),
                deliverables=tmpl_def.get("deliverables", []),
                skill_names=tmpl_def.get("skill_names", []),
                origin_pack_id=pack_id,
                origin_release_id=release_id,
                origin_component_id=tmpl_def.get("logical_id", ""),
                created_by=installed_by,
            )
            self.db.add(tmpl)

        # Create installation record
        install = SkillPackInstallation(
            org_id=org_id,
            pack_id=pack_id,
            release_id=release_id,
            installed_version=release_version,
            status=InstallStatus.ACTIVE,
            installed_by=installed_by,
        )
        self.db.add(install)

        # Atomic install count increment (avoid lost-update race)
        from sqlalchemy import update
        await self.db.execute(
            update(SkillPack)
            .where(SkillPack.id == pack_id)
            .values(install_count=SkillPack.install_count + 1)
        )

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise AppError("ALREADY_INSTALLED", "Pack already installed in this organization", 409) from None

        # Fire webhook event
        try:
            from app.services.webhook import WebhookService
            webhook_svc = WebhookService(self.db)
            await webhook_svc.trigger_event(
                org_id,
                "pack.installed",
                {"pack_id": pack_id, "version": release_version, "org_id": org_id},
            )
        except Exception:
            log.warning("webhook_trigger_failed", webhook_event="pack.installed")

        log.info(
            "pack_installed",
            org_id=org_id,
            pack_id=pack_id,
            version=release_version,
            skills=len(skill_id_map),
        )
        return install

    # ── List / Get ──

    async def list_installations(
        self, org_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[SkillPackInstallation], int]:
        base = select(SkillPackInstallation).where(
            SkillPackInstallation.org_id == org_id,
            SkillPackInstallation.status != InstallStatus.REMOVED,
        )
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(SkillPackInstallation.installed_at.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_installation(self, install_id: str, org_id: str) -> SkillPackInstallation:
        inst = await self.db.get(SkillPackInstallation, install_id)
        if inst is None or inst.org_id != org_id or inst.status == InstallStatus.REMOVED:
            raise InstallationNotFoundError()
        return inst

    # ── Update check ──

    async def check_update(self, install_id: str, org_id: str) -> dict:
        inst = await self.get_installation(install_id, org_id)
        if inst.pack_id is None:
            return {"update_available": False, "reason": "source_unavailable"}

        if inst.status == InstallStatus.FORKED:
            return {"update_available": False, "reason": "forked"}

        # Find latest release by semver
        all_r = await self.db.execute(
            select(SkillPackRelease).where(SkillPackRelease.pack_id == inst.pack_id)
        )
        all_releases = list(all_r.scalars().all())
        latest = max(all_releases, key=lambda r: _parse_semver(r.version)) if all_releases else None
        if latest is None or latest.version == inst.installed_version:
            return {"update_available": False, "installed_version": inst.installed_version}

        return {
            "update_available": True,
            "installed_version": inst.installed_version,
            "latest_version": latest.version,
        }

    # ── Diff ──

    async def compute_diff(self, install_id: str, org_id: str, target_version: str) -> dict:
        inst = await self.get_installation(install_id, org_id)
        if inst.status == InstallStatus.FORKED:
            raise AppError("INSTALL_FORKED", "Cannot diff a forked installation", 422)
        if inst.release_id is None:
            raise AppError("NO_RELEASE", "Installation has no release reference", 422)

        old_release = await self.db.get(SkillPackRelease, inst.release_id)
        new_release_r = await self.db.execute(
            select(SkillPackRelease).where(
                SkillPackRelease.pack_id == inst.pack_id,
                SkillPackRelease.version == target_version,
            )
        )
        new_release = new_release_r.scalar_one_or_none()
        if new_release is None:
            raise AppError("RELEASE_NOT_FOUND", f"Version {target_version} not found", 404)

        old_m = old_release.manifest if old_release and old_release.manifest else {}
        new_m = new_release.manifest if new_release.manifest else {}

        if not old_m and not new_m:
            return {"added": [], "changed": [], "removed": [], "conflicts": []}

        old_skills = {s["logical_id"]: s for s in old_m.get("skills", [])}
        new_skills = {s["logical_id"]: s for s in new_m.get("skills", [])}
        old_tmpls = {t["logical_id"]: t for t in old_m.get("project_templates", [])}
        new_tmpls = {t["logical_id"]: t for t in new_m.get("project_templates", [])}

        diff: dict = {"added": [], "changed": [], "removed": [], "conflicts": []}

        # Added
        for lid in set(new_skills) - set(old_skills):
            diff["added"].append({"type": "skill", "logical_id": lid, "name": new_skills[lid]["name"]})
        for lid in set(new_tmpls) - set(old_tmpls):
            diff["added"].append({"type": "template", "logical_id": lid, "name": new_tmpls[lid]["name"]})

        # Removed
        for lid in set(old_skills) - set(new_skills):
            diff["removed"].append({"type": "skill", "logical_id": lid, "name": old_skills[lid]["name"]})
        for lid in set(old_tmpls) - set(new_tmpls):
            diff["removed"].append({"type": "template", "logical_id": lid, "name": old_tmpls[lid]["name"]})

        # Batch-load locally_modified flags (exclude archived — they don't conflict)
        skill_mod_r = await self.db.execute(
            select(Skill.origin_component_id, Skill.locally_modified).where(
                Skill.origin_pack_id == inst.pack_id,
                Skill.org_id == org_id,
                Skill.status != ContentStatus.ARCHIVED,
            )
        )
        skill_modified_map = {row[0]: row[1] for row in skill_mod_r.all()}

        tmpl_mod_r = await self.db.execute(
            select(ProjectTemplate.origin_component_id, ProjectTemplate.locally_modified).where(
                ProjectTemplate.origin_pack_id == inst.pack_id,
                ProjectTemplate.org_id == org_id,
                ProjectTemplate.status != ContentStatus.ARCHIVED,
            )
        )
        tmpl_modified_map = {row[0]: row[1] for row in tmpl_mod_r.all()}

        # Changed
        for lid in set(old_skills) & set(new_skills):
            if old_skills[lid] != new_skills[lid]:
                if skill_modified_map.get(lid):
                    diff["conflicts"].append({
                        "type": "skill", "logical_id": lid,
                        "name": new_skills[lid]["name"], "reason": "locally_modified",
                    })
                else:
                    diff["changed"].append({
                        "type": "skill", "logical_id": lid,
                        "name": new_skills[lid]["name"],
                    })

        for lid in set(old_tmpls) & set(new_tmpls):
            if old_tmpls[lid] != new_tmpls[lid]:
                if tmpl_modified_map.get(lid):
                    diff["conflicts"].append({
                        "type": "template", "logical_id": lid,
                        "name": new_tmpls[lid]["name"], "reason": "locally_modified",
                    })
                else:
                    diff["changed"].append({
                        "type": "template", "logical_id": lid,
                        "name": new_tmpls[lid]["name"],
                    })

        return diff

    # ── Fork ──

    async def fork(self, install_id: str, org_id: str) -> SkillPackInstallation:
        inst = await self.get_installation(install_id, org_id)
        if inst.status == InstallStatus.FORKED:
            raise AppError("ALREADY_FORKED", "Installation is already forked", 422)

        # Remove origin tracking from all installed components
        for model in (Skill, Exercise, SkillCategory, ProjectTemplate):
            result = await self.db.execute(
                select(model).where(
                    model.origin_pack_id == inst.pack_id,
                    model.org_id == org_id,
                )
            )
            for component in result.scalars():
                component.origin_pack_id = None
                component.origin_release_id = None
                component.origin_component_id = None
                component.locally_modified = False

        inst.status = InstallStatus.FORKED
        await self.db.flush()

        # Fire webhook event
        try:
            from app.services.webhook import WebhookService
            webhook_svc = WebhookService(self.db)
            await webhook_svc.trigger_event(
                org_id,
                "pack.forked",
                {"install_id": install_id, "org_id": org_id, "pack_id": inst.pack_id},
            )
        except Exception:
            log.warning("webhook_trigger_failed", webhook_event="pack.forked")

        log.info("pack_forked", install_id=install_id, org_id=org_id)
        return inst

    # ── Upgrade ──

    async def upgrade(
        self,
        install_id: str,
        org_id: str,
        target_version: str,
        installed_by: str,
    ) -> SkillPackInstallation:
        """Upgrade (or rollback) an installation to any version."""
        inst = await self.get_installation(install_id, org_id)
        if inst.status == InstallStatus.FORKED:
            raise AppError("INSTALL_FORKED", "Cannot upgrade a forked installation", 422)
        if inst.pack_id is None:
            raise AppError("NO_SOURCE", "Installation source pack is unavailable", 422)

        # Get target release
        release_r = await self.db.execute(
            select(SkillPackRelease).where(
                SkillPackRelease.pack_id == inst.pack_id,
                SkillPackRelease.version == target_version,
            )
        )
        release = release_r.scalar_one_or_none()
        if release is None:
            raise AppError("RELEASE_NOT_FOUND", f"Version {target_version} not found", 404)

        # Get current release manifest
        if inst.release_id is None:
            raise AppError("NO_RELEASE", "Installation has no release reference", 422)
        current_release = await self.db.get(SkillPackRelease, inst.release_id)
        if current_release is None:
            raise AppError("NO_RELEASE", "Current release not found", 422)

        old_m = current_release.manifest
        new_m = release.manifest

        old_skills = {s["logical_id"]: s for s in old_m.get("skills", [])}
        new_skills = {s["logical_id"]: s for s in new_m.get("skills", [])}
        old_tmpls = {t["logical_id"]: t for t in old_m.get("project_templates", [])}
        new_tmpls = {t["logical_id"]: t for t in new_m.get("project_templates", [])}

        pack_id = inst.pack_id

        # ---- Create categories needed by ADDED skills ----
        old_cats = {c["logical_id"]: c for c in old_m.get("categories", [])}
        new_cats = {c["logical_id"]: c for c in new_m.get("categories", [])}
        cat_id_map: dict[str, str] = {}  # logical_id -> existing or new category ULID

        # Map existing categories (already installed)
        for cat_lid in new_cats:
            if cat_lid in old_cats:
                # Category was already installed — find its current id
                existing_cat_r = await self.db.execute(
                    select(SkillCategory.id).where(
                        SkillCategory.origin_component_id == cat_lid,
                        SkillCategory.origin_pack_id == pack_id,
                        SkillCategory.org_id == org_id,
                    )
                )
                existing_cat_id = existing_cat_r.scalar_one_or_none()
                if existing_cat_id:
                    cat_id_map[cat_lid] = existing_cat_id

        # Create NEW categories
        for cat_lid in set(new_cats) - set(old_cats):
            import secrets as _cat_secrets
            cat_def = new_cats[cat_lid]
            cat = SkillCategory(
                org_id=org_id,
                name=cat_def["name"],
                slug=f"{cat_def['slug'][:90]}-{_cat_secrets.token_hex(3)}",
                sort_order=cat_def.get("sort_order", 0),
                status=ContentStatus.PUBLISHED,
                origin_pack_id=pack_id,
                origin_release_id=release.id,
                origin_component_id=cat_lid,
                created_by=installed_by,
            )
            self.db.add(cat)
            await self.db.flush()
            cat_id_map[cat_lid] = cat.id

        # ---- Handle ADDED skills ----
        for lid in set(new_skills) - set(old_skills):
            skill_def = new_skills[lid]
            import secrets as _secrets

            cat_logical = skill_def.get("category_logical_id")
            category_id = cat_id_map.get(cat_logical) if cat_logical else None

            skill = Skill(
                org_id=org_id,
                category_id=category_id,
                name=skill_def["name"],
                slug=f"{skill_def.get('slug', skill_def['name'].lower().replace(' ', '-')[:200])[:190]}-{_secrets.token_hex(3)}",
                description=skill_def.get("description", ""),
                learning_content=skill_def.get("learning_content"),
                difficulty=skill_def.get("difficulty", "beginner"),
                estimated_minutes=skill_def.get("estimated_minutes"),
                tags=skill_def.get("tags", []),
                sort_order=skill_def.get("sort_order", 0),
                status=ContentStatus.PUBLISHED,
                origin_pack_id=pack_id,
                origin_release_id=release.id,
                origin_component_id=lid,
                created_by=installed_by,
            )
            self.db.add(skill)
            await self.db.flush()

            for ex_def in skill_def.get("exercises", []):
                exercise = Exercise(
                    org_id=org_id,
                    skill_id=skill.id,
                    title=ex_def["title"],
                    description=ex_def.get("description", ""),
                    type=ExerciseType(ex_def.get("type", "text_answer")),
                    config=ex_def.get("config", {}),
                    max_score=ex_def.get("max_score", 100),
                    sort_order=ex_def.get("sort_order", 0),
                    status=ContentStatus.PUBLISHED,
                    origin_pack_id=pack_id,
                    origin_release_id=release.id,
                    origin_component_id=ex_def.get("logical_id", ""),
                    created_by=installed_by,
                )
                self.db.add(exercise)

        # Flush so new skill IDs are available for prerequisite creation
        await self.db.flush()

        # ---- Create prerequisites for ADDED skills ----
        # Build a unified skill_id_map: logical_id -> actual skill ULID
        # Includes both newly created skills AND existing installed skills
        skill_id_map: dict[str, str] = {}
        # Existing installed skills (from batch-load below, but we need them now)
        existing_skills_r = await self.db.execute(
            select(Skill).where(
                Skill.origin_pack_id == pack_id,
                Skill.org_id == org_id,
                Skill.status != ContentStatus.ARCHIVED,
            )
        )
        for s in existing_skills_r.scalars().all():
            if s.origin_component_id:
                skill_id_map[s.origin_component_id] = s.id

        # Create prerequisite rows for added skills
        for lid in set(new_skills) - set(old_skills):
            skill_def = new_skills[lid]
            for prereq_logical in skill_def.get("prerequisites", []):
                if prereq_logical in skill_id_map and lid in skill_id_map:
                    prereq = SkillPrerequisite(
                        skill_id=skill_id_map[lid],
                        prerequisite_id=skill_id_map[prereq_logical],
                    )
                    self.db.add(prereq)

        # Batch-load all installed skills and templates for this pack (avoid N+1)
        all_skills_r = await self.db.execute(
            select(Skill).where(
                Skill.origin_pack_id == pack_id,
                Skill.org_id == org_id,
                Skill.status != ContentStatus.ARCHIVED,
            )
        )
        skills_by_component = {s.origin_component_id: s for s in all_skills_r.scalars().all()}

        all_tmpls_r = await self.db.execute(
            select(ProjectTemplate).where(
                ProjectTemplate.origin_pack_id == pack_id,
                ProjectTemplate.org_id == org_id,
                ProjectTemplate.status != ContentStatus.ARCHIVED,
            )
        )
        tmpls_by_component = {t.origin_component_id: t for t in all_tmpls_r.scalars().all()}

        # ---- Handle CHANGED skills (update in place if not locally modified) ----
        for lid in set(old_skills) & set(new_skills):
            if old_skills[lid] != new_skills[lid]:
                existing = skills_by_component.get(lid)
                if existing and not existing.locally_modified:
                    skill_def = new_skills[lid]
                    existing.name = skill_def["name"]
                    existing.description = skill_def.get("description", "")
                    existing.learning_content = skill_def.get("learning_content")
                    existing.difficulty = skill_def.get("difficulty", "beginner")
                    existing.estimated_minutes = skill_def.get("estimated_minutes")
                    existing.tags = skill_def.get("tags", [])
                    existing.origin_release_id = release.id
                    # Update category_id if skill moved to a different category
                    cat_logical = skill_def.get("category_logical_id")
                    if cat_logical and cat_logical in cat_id_map:
                        existing.category_id = cat_id_map[cat_logical]

                    # ---- Sync exercises for changed skill ----
                    new_exercises = {
                        e["logical_id"]: e for e in skill_def.get("exercises", [])
                    }
                    existing_ex_r = await self.db.execute(
                        select(Exercise).where(
                            Exercise.skill_id == existing.id,
                            Exercise.status != ContentStatus.ARCHIVED,
                        )
                    )
                    existing_exercises = list(existing_ex_r.scalars().all())
                    ex_by_origin = {}
                    for ex in existing_exercises:
                        if ex.origin_component_id:
                            ex_by_origin[ex.origin_component_id] = ex

                    # Update existing / add new exercises
                    for ex_lid, ex_def in new_exercises.items():
                        ex_existing = ex_by_origin.get(ex_lid)
                        if ex_existing and not ex_existing.locally_modified:
                            ex_existing.title = ex_def.get("title", ex_existing.title)
                            ex_existing.description = ex_def.get("description", "")
                            ex_existing.type = ExerciseType(ex_def.get("type", "text_answer"))
                            ex_existing.config = ex_def.get("config", {})
                            ex_existing.max_score = ex_def.get("max_score", 100)
                            ex_existing.sort_order = ex_def.get("sort_order", 0)
                        elif ex_existing is None:
                            new_ex = Exercise(
                                org_id=org_id,
                                skill_id=existing.id,
                                title=ex_def.get("title", ""),
                                description=ex_def.get("description", ""),
                                type=ExerciseType(ex_def.get("type", "text_answer")),
                                config=ex_def.get("config", {}),
                                max_score=ex_def.get("max_score", 100),
                                sort_order=ex_def.get("sort_order", 0),
                                status=ContentStatus.PUBLISHED,
                                created_by=installed_by,
                                origin_pack_id=pack_id,
                                origin_component_id=ex_lid,
                                origin_release_id=release.id,
                            )
                            self.db.add(new_ex)

                    # Archive exercises removed in new version
                    for ex in existing_exercises:
                        if (
                            ex.origin_component_id
                            and ex.origin_component_id not in new_exercises
                            and not ex.locally_modified
                        ):
                            ex.status = ContentStatus.ARCHIVED

        # ---- Handle REMOVED skills (archive, preserve learner data) ----
        for lid in set(old_skills) - set(new_skills):
            existing = skills_by_component.get(lid)
            if existing:
                existing.status = ContentStatus.ARCHIVED
                # Also archive the skill's exercises
                ex_r = await self.db.execute(
                    select(Exercise).where(
                        Exercise.skill_id == existing.id,
                        Exercise.status != ContentStatus.ARCHIVED,
                    )
                )
                for ex in ex_r.scalars():
                    ex.status = ContentStatus.ARCHIVED

        # ---- Handle ADDED templates ----
        for lid in set(new_tmpls) - set(old_tmpls):
            tmpl_def = new_tmpls[lid]
            tmpl = ProjectTemplate(
                org_id=org_id,
                name=tmpl_def["name"],
                description=tmpl_def.get("description", ""),
                instructions=tmpl_def.get("instructions", ""),
                project_type=tmpl_def.get("project_type", "general"),
                difficulty=tmpl_def.get("difficulty", "intermediate"),
                suggested_minutes=tmpl_def.get("suggested_minutes"),
                max_score=tmpl_def.get("max_score", 100),
                rubric=tmpl_def.get("rubric", [{"criterion": "Overall", "max_score": 100}]),
                deliverables=tmpl_def.get("deliverables", []),
                skill_names=tmpl_def.get("skill_names", []),
                origin_pack_id=pack_id,
                origin_release_id=release.id,
                origin_component_id=lid,
                created_by=installed_by,
            )
            self.db.add(tmpl)

        # ---- Handle CHANGED templates ----
        for lid in set(old_tmpls) & set(new_tmpls):
            if old_tmpls[lid] != new_tmpls[lid]:
                existing = tmpls_by_component.get(lid)
                if existing and not existing.locally_modified:
                    tmpl_def = new_tmpls[lid]
                    existing.name = tmpl_def["name"]
                    existing.description = tmpl_def.get("description", "")
                    existing.instructions = tmpl_def.get("instructions", "")
                    existing.project_type = tmpl_def.get("project_type", "general")
                    existing.difficulty = tmpl_def.get("difficulty", "intermediate")
                    existing.suggested_minutes = tmpl_def.get("suggested_minutes")
                    existing.max_score = tmpl_def.get("max_score", 100)
                    existing.rubric = tmpl_def.get("rubric", [{"criterion": "Overall", "max_score": 100}])
                    existing.deliverables = tmpl_def.get("deliverables", [])
                    existing.skill_names = tmpl_def.get("skill_names", [])
                    existing.origin_release_id = release.id

        # ---- Handle REMOVED templates (archive) ----
        for lid in set(old_tmpls) - set(new_tmpls):
            existing = tmpls_by_component.get(lid)
            if existing:
                existing.status = ContentStatus.ARCHIVED

        # Update installation record
        inst.release_id = release.id
        inst.installed_version = target_version
        await self.db.flush()

        log.info(
            "pack_upgraded",
            install_id=install_id,
            org_id=org_id,
            from_version=current_release.version,
            to_version=target_version,
        )
        return inst

    # ── Remove ──

    async def remove(self, install_id: str, org_id: str) -> None:
        inst = await self.get_installation(install_id, org_id)
        was_forked = inst.status == InstallStatus.FORKED
        inst.status = InstallStatus.REMOVED
        await self.db.flush()

        # Decrement install_count atomically (floor at 0)
        if inst.pack_id:
            from sqlalchemy import update

            await self.db.execute(
                update(SkillPack)
                .where(SkillPack.id == inst.pack_id)
                .values(install_count=func.greatest(SkillPack.install_count - 1, 0))
            )

        # Archive installed components — but NOT if the installation was forked.
        # fork() nulls origin_pack_id (severing tracking), so the WHERE clause
        # wouldn't match anything. More importantly, fork is a deliberate choice
        # to keep the content independently, so archiving would be wrong.
        if not was_forked and inst.pack_id:
            from sqlalchemy import update as _update

            for model in [Skill, Exercise, SkillCategory]:
                await self.db.execute(
                    _update(model)
                    .where(
                        model.origin_pack_id == inst.pack_id,
                        model.org_id == inst.org_id,
                        model.status != ContentStatus.ARCHIVED,
                    )
                    .values(status=ContentStatus.ARCHIVED)
                )
            await self.db.execute(
                _update(ProjectTemplate)
                .where(
                    ProjectTemplate.origin_pack_id == inst.pack_id,
                    ProjectTemplate.org_id == inst.org_id,
                    ProjectTemplate.status != ContentStatus.ARCHIVED,
                )
                .values(status=ContentStatus.ARCHIVED)
            )

            await self.db.flush()

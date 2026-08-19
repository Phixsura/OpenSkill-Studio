"""Pack installation, upgrade, diff, and fork service."""

import structlog
from sqlalchemy import func, select
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
    PackVisibility,
    SkillPack,
    SkillPackInstallation,
    SkillPackRelease,
)

log = structlog.get_logger()


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
                select(SkillPackRelease)
                .where(SkillPackRelease.pack_id == pack_id)
                .order_by(SkillPackRelease.released_at.desc())
                .limit(1)
            )
            release = release_r.scalar_one_or_none()

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
                # Category might not exist yet — skip prerequisite for now
                continue

            import secrets as _secrets

            skill = Skill(
                org_id=org_id,
                category_id=category_id,
                name=skill_def["name"],
                slug=skill_def.get("slug", skill_def["name"].lower().replace(" ", "-")[:200]),
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

        await self.db.flush()

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

        # Find latest release
        latest_r = await self.db.execute(
            select(SkillPackRelease)
            .where(SkillPackRelease.pack_id == inst.pack_id)
            .order_by(SkillPackRelease.released_at.desc())
            .limit(1)
        )
        latest = latest_r.scalar_one_or_none()
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

        old_m = old_release.manifest
        new_m = new_release.manifest

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

        # Changed
        for lid in set(old_skills) & set(new_skills):
            if old_skills[lid] != new_skills[lid]:
                # Check if locally modified
                local_r = await self.db.execute(
                    select(Skill.locally_modified).where(
                        Skill.origin_component_id == lid,
                        Skill.origin_pack_id == inst.pack_id,
                        Skill.org_id == org_id,
                    )
                )
                local = local_r.scalar_one_or_none()
                if local:
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
                local_r = await self.db.execute(
                    select(ProjectTemplate.locally_modified).where(
                        ProjectTemplate.origin_component_id == lid,
                        ProjectTemplate.origin_pack_id == inst.pack_id,
                        ProjectTemplate.org_id == org_id,
                    )
                )
                local = local_r.scalar_one_or_none()
                if local:
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

        log.info("pack_forked", install_id=install_id, org_id=org_id)
        return inst

    # ── Remove ──

    async def remove(self, install_id: str, org_id: str) -> None:
        inst = await self.get_installation(install_id, org_id)
        inst.status = InstallStatus.REMOVED
        await self.db.flush()

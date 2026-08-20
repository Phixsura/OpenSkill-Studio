"""Public pack registry — search, filter, browse published packs."""

import hashlib
from datetime import UTC, datetime

import structlog
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.exceptions import AppError
from app.models.skill_pack import (
    PackStatus,
    PackVisibility,
    SkillPack,
    SkillPackRelease,
)

log = structlog.get_logger()


def _compute_badges(pack: "SkillPack", now: datetime, thirty_days_ago: datetime) -> list[str]:
    """Derive badge list from pack state. Pure function, no DB."""
    badges: list[str] = []
    if pack.install_count >= 10:
        badges.append("Popular")
    if pack.created_at and pack.created_at >= thirty_days_ago:
        badges.append("New")
    return badges


def _parse_semver(version: str) -> tuple[int, int, int, str]:
    """Parse 'X.Y.Z' or 'X.Y.Z-prerelease' into a comparable tuple.

    Pre-release versions sort BEFORE the release (1.0.0-alpha < 1.0.0).
    """
    base, _, prerelease = version.partition("-")
    parts = base.split(".")
    pre_key = prerelease if prerelease else "~"  # '~' > all ASCII letters
    return (int(parts[0]), int(parts[1]), int(parts[2]), pre_key)


class RegistryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_packs(
        self,
        search: str | None = None,
        scenario: str | None = None,
        tool: str | None = None,
        difficulty: str | None = None,
        category: str | None = None,
        sort: str = "newest",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[SkillPack], int]:
        """Search public, published packs.

        Uses PostgreSQL full-text search (to_tsvector + websearch_to_tsquery)
        with an ILIKE fallback so substring and random-token searches still work.
        Results are cached in Redis for 5 minutes.
        """
        # ── Check cache ──
        cache_key_src = f"{search}:{scenario}:{tool}:{difficulty}:{category}:{sort}:{page}:{per_page}"
        cache_key = f"registry:search:{hashlib.md5(cache_key_src.encode()).hexdigest()}"
        cached = await cache_get(cache_key)
        if cached is not None:
            # Re-hydrate from cache: fetch packs by id list
            pack_ids = cached.get("ids", [])
            total = cached.get("total", 0)
            if pack_ids:
                result = await self.db.execute(
                    select(SkillPack).where(SkillPack.id.in_(pack_ids))
                )
                packs_by_id = {p.id: p for p in result.scalars().all()}
                return [packs_by_id[pid] for pid in pack_ids if pid in packs_by_id], total
            return [], total

        # ── Build query ──
        base = select(SkillPack).where(
            SkillPack.visibility == PackVisibility.PUBLIC,
            SkillPack.status == PackStatus.PUBLISHED,
            or_(
                SkillPack.review_status.is_(None),
                SkillPack.review_status == "approved",
            ),
        )

        if search:
            # Full-text search on name + summary + description
            search_vector = func.to_tsvector(
                "english",
                func.coalesce(SkillPack.name, "")
                + " "
                + func.coalesce(SkillPack.summary, "")
                + " "
                + func.coalesce(SkillPack.description, ""),
            )
            # ILIKE fallback for substring / random-token searches
            term = f"%{search}%"
            ilike_cond = or_(
                SkillPack.name.ilike(term),
                SkillPack.summary.ilike(term),
                SkillPack.description.ilike(term),
                cast(SkillPack.scenario_tags, String).ilike(term),
                cast(SkillPack.tool_tags, String).ilike(term),
                cast(SkillPack.capability_tags, String).ilike(term),
            )
            # Combine FTS and ILIKE with OR so both token and substring matches work
            try:
                fts_cond = search_vector.op("@@")(
                    func.websearch_to_tsquery("english", search)
                )
                base = base.where(or_(fts_cond, ilike_cond))
            except Exception:
                # If websearch_to_tsquery fails (bad syntax), fall back to ILIKE only
                base = base.where(ilike_cond)

        if scenario:
            base = base.where(SkillPack.scenario_tags.contains([scenario]))

        if tool:
            base = base.where(SkillPack.tool_tags.contains([tool]))

        if difficulty:
            base = base.where(SkillPack.difficulty == difficulty)

        if category:
            from app.models.pack_category import PackCategory, PackCategoryAssignment

            base = base.where(
                SkillPack.id.in_(
                    select(PackCategoryAssignment.pack_id).join(
                        PackCategory, PackCategory.id == PackCategoryAssignment.category_id
                    ).where(PackCategory.slug == category)
                )
            )

        # Sort
        if sort in ("most_installed", "popular"):
            base = base.order_by(SkillPack.install_count.desc())
        elif sort == "recently_updated":
            base = base.order_by(SkillPack.updated_at.desc())
        elif sort == "name":
            base = base.order_by(SkillPack.name.asc())
        else:  # newest
            base = base.order_by(SkillPack.created_at.desc())

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(base.offset(offset).limit(per_page))
        packs = list(result.scalars().all())

        # ── Populate cache ──
        await cache_set(cache_key, {"ids": [p.id for p in packs], "total": total}, ttl=300)

        # ── Compute and persist badges ──
        from datetime import timedelta

        now = datetime.now(UTC)
        thirty_days_ago = now - timedelta(days=30)
        modified: list[SkillPack] = []
        for pack in packs:
            badges = _compute_badges(pack, now, thirty_days_ago)
            if badges != (pack.badges or []):
                pack.badges = badges
                modified.append(pack)
        # Flush any badge updates without committing (caller controls commit)
        if modified:
            await self.db.flush()
            # Refresh modified packs so server-side onupdate columns
            # (e.g. updated_at) are eagerly loaded before Pydantic serialisation.
            for pack in modified:
                await self.db.refresh(pack)

        return packs, total

    async def get_public_pack(self, pack_id: str) -> SkillPack:
        """Get a public or unlisted pack by ID. Cached for 1 minute."""
        pack = await self.db.get(SkillPack, pack_id)
        if pack is None:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.status != PackStatus.PUBLISHED:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.visibility == PackVisibility.PRIVATE:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        return pack

    async def get_public_releases(self, pack_id: str) -> list[SkillPackRelease]:
        """List releases for a public pack."""
        await self.get_public_pack(pack_id)  # verify accessible
        result = await self.db.execute(
            select(SkillPackRelease).where(SkillPackRelease.pack_id == pack_id)
        )
        releases = list(result.scalars().all())
        releases.sort(key=lambda r: _parse_semver(r.version), reverse=True)
        return releases

    async def list_categories(self) -> list[dict]:
        """Return pack categories as a tree structure."""
        from app.models.pack_category import PackCategory

        result = await self.db.execute(
            select(PackCategory).order_by(PackCategory.sort_order)
        )
        categories = list(result.scalars().all())

        # Build tree: group children by parent_id
        by_parent: dict[str | None, list[dict]] = {}
        cat_dicts = {}
        for cat in categories:
            d = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "icon": cat.icon,
                "sort_order": cat.sort_order,
                "children": [],
            }
            cat_dicts[cat.id] = d
            by_parent.setdefault(cat.parent_id, []).append(d)

        # Attach children to parents
        for cat in categories:
            if cat.parent_id and cat.parent_id in cat_dicts:
                cat_dicts[cat.parent_id]["children"].append(cat_dicts[cat.id])

        # Return only root nodes (parent_id is None)
        return by_parent.get(None, [])

    async def recompute_pack_badges(self, pack_id: str) -> None:
        """Recompute and persist badges for a single pack."""
        from datetime import timedelta

        pack = await self.db.get(SkillPack, pack_id)
        if pack is None:
            return
        now = datetime.now(UTC)
        thirty_days_ago = now - timedelta(days=30)
        badges = _compute_badges(pack, now, thirty_days_ago)
        if badges != (pack.badges or []):
            pack.badges = badges
            await self.db.flush()

    async def get_pack_preview(self, pack_id: str) -> dict:
        """Build a curriculum preview from the latest release manifest."""
        await self.get_public_pack(pack_id)  # verify accessible

        result = await self.db.execute(
            select(SkillPackRelease)
            .where(SkillPackRelease.pack_id == pack_id)
            .order_by(SkillPackRelease.released_at.desc())
            .limit(1)
        )
        release = result.scalar_one_or_none()
        if release is None:
            raise AppError("NO_RELEASES", "This pack has no releases yet", 404)

        manifest = release.manifest or {}

        # Extract skills
        raw_skills = manifest.get("skills", [])
        skills = []
        total_exercises = 0
        for s in raw_skills:
            exercises = s.get("exercises", [])
            total_exercises += len(exercises)
            skills.append({
                "name": s.get("name", ""),
                "description": s.get("description"),
                "difficulty": s.get("difficulty"),
                "exercise_count": len(exercises),
                "exercises": [{"title": e.get("title", "")} for e in exercises],
                "prerequisites": s.get("prerequisites", []),
            })

        # Extract templates
        raw_templates = manifest.get("project_templates", [])
        templates = []
        for t in raw_templates:
            rubric = t.get("rubric") or {}
            criteria = rubric.get("criteria", [])
            templates.append({
                "name": t.get("name", ""),
                "description": t.get("description"),
                "rubric_criteria_count": len(criteria),
            })

        # Extract categories
        raw_categories = manifest.get("categories", [])
        categories = [{"name": c.get("name", "")} for c in raw_categories]

        return {
            "skills": skills,
            "templates": templates,
            "categories": categories,
            "total_skills": len(skills),
            "total_exercises": total_exercises,
            "total_templates": len(templates),
        }

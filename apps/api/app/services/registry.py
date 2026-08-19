"""Public pack registry — search, filter, browse published packs."""

import hashlib

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
        cache_key_src = f"{search}:{scenario}:{tool}:{difficulty}:{sort}:{page}:{per_page}"
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

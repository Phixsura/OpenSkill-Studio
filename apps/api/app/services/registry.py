"""Public pack registry — search, filter, browse published packs."""

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.skill_pack import (
    PackStatus,
    PackVisibility,
    SkillPack,
    SkillPackRelease,
)

log = structlog.get_logger()


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
        """Search public, published packs."""
        base = select(SkillPack).where(
            SkillPack.visibility == PackVisibility.PUBLIC,
            SkillPack.status == PackStatus.PUBLISHED,
        )

        if search:
            term = f"%{search}%"
            base = base.where(
                or_(
                    SkillPack.name.ilike(term),
                    SkillPack.summary.ilike(term),
                    SkillPack.description.ilike(term),
                )
            )

        if scenario:
            base = base.where(SkillPack.scenario_tags.contains([scenario]))

        if tool:
            base = base.where(SkillPack.tool_tags.contains([tool]))

        if difficulty:
            base = base.where(SkillPack.difficulty == difficulty)

        # Sort
        if sort == "most_installed":
            base = base.order_by(SkillPack.install_count.desc())
        elif sort == "recently_updated":
            base = base.order_by(SkillPack.updated_at.desc())
        else:  # newest
            base = base.order_by(SkillPack.created_at.desc())

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        offset = (page - 1) * per_page
        result = await self.db.execute(base.offset(offset).limit(per_page))
        return list(result.scalars().all()), total

    async def get_public_pack(self, pack_id: str) -> SkillPack:
        """Get a public or unlisted pack by ID."""
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
            select(SkillPackRelease)
            .where(SkillPackRelease.pack_id == pack_id)
            .order_by(SkillPackRelease.released_at.desc())
        )
        return list(result.scalars().all())

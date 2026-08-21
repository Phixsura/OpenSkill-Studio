"""Cross-organization pack sharing service."""

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.organization import Organization, OrgStatus
from app.models.pack_share import PackShare
from app.models.skill_pack import PackStatus, SkillPack

log = structlog.get_logger()

MAX_SHARES_PER_PACK = 100


class PackSharingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def share_pack(
        self,
        org_id: str,
        pack_id: str,
        target_org_id: str,
        user_id: str,
    ) -> PackShare:
        """Share a pack with another organization."""
        # Verify pack exists and belongs to this org
        pack = await self.db.get(SkillPack, pack_id)
        if pack is None or pack.owner_org_id != org_id:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.status != PackStatus.PUBLISHED:
            raise AppError("PACK_NOT_PUBLISHED", "Only published packs can be shared", 422)
        if not pack.sharing_enabled:
            raise AppError("SHARING_DISABLED", "Sharing is not enabled for this pack", 422)
        if target_org_id == org_id:
            raise AppError("SELF_SHARE", "Cannot share a pack with its own organization", 422)

        # Verify target org exists
        target_org = await self.db.get(Organization, target_org_id)
        if target_org is None or target_org.status == OrgStatus.ARCHIVED:
            raise AppError("TARGET_ORG_NOT_FOUND", "Target organization not found", 404)

        # Check share limit
        existing_count_r = await self.db.execute(
            select(PackShare).where(PackShare.pack_id == pack_id)
        )
        existing = list(existing_count_r.scalars().all())
        if len(existing) >= MAX_SHARES_PER_PACK:
            raise AppError(
                "SHARE_LIMIT_REACHED",
                f"Maximum {MAX_SHARES_PER_PACK} shares per pack",
                422,
            )

        share = PackShare(
            pack_id=pack_id,
            target_org_id=target_org_id,
            shared_by=user_id,
        )
        self.db.add(share)

        try:
            await self.db.flush()
        except IntegrityError:
            # Use savepoint rollback — don't roll back the whole session
            await self.db.rollback()
            raise AppError(
                "ALREADY_SHARED", "Pack is already shared with this organization", 409
            ) from None

        log.info("pack_shared", pack_id=pack_id, target_org_id=target_org_id)
        return share

    async def list_shared_packs(self, org_id: str) -> list[SkillPack]:
        """List packs shared with this org."""
        result = await self.db.execute(
            select(SkillPack)
            .join(PackShare, PackShare.pack_id == SkillPack.id)
            .where(
                PackShare.target_org_id == org_id,
                SkillPack.status == PackStatus.PUBLISHED,
            )
            .order_by(SkillPack.name)
        )
        return list(result.scalars().all())

    async def revoke_share(
        self,
        org_id: str,
        pack_id: str,
        target_org_id: str,
    ) -> None:
        """Revoke a pack share — only the owner org can revoke."""
        # Verify the pack belongs to this org
        pack = await self.db.get(SkillPack, pack_id)
        if pack is None or pack.owner_org_id != org_id:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)

        result = await self.db.execute(
            select(PackShare).where(
                PackShare.pack_id == pack_id,
                PackShare.target_org_id == target_org_id,
            )
        )
        share = result.scalar_one_or_none()
        if share is None:
            raise AppError("SHARE_NOT_FOUND", "Share not found", 404)

        await self.db.delete(share)
        await self.db.flush()
        log.info("pack_share_revoked", pack_id=pack_id, target_org_id=target_org_id)

"""Cross-organization pack sharing endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.pack_share import PackShare
from app.models.skill_pack import PackStatus, SkillPack
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.skill_pack import SkillPackResponse

router = APIRouter(tags=["Pack Sharing"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


class SharePackRequest(BaseModel):
    target_org_id: str


class PackShareResponse(BaseModel):
    id: str
    pack_id: str
    target_org_id: str
    shared_by: str
    shared_at: str

    model_config = {"from_attributes": True}


@router.post(
    "/orgs/{org_id}/packs/{pack_id}/share",
    response_model=DataResponse[PackShareResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def share_pack(
    org_id: str,
    pack_id: str,
    body: SharePackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Share a pack with another organization."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)

    # Verify pack exists and belongs to this org
    pack = await db.get(SkillPack, pack_id)
    if pack is None or pack.owner_org_id != org_id:
        raise HTTPException(status_code=404, detail="Pack not found")
    if pack.status != PackStatus.PUBLISHED:
        raise HTTPException(status_code=422, detail="Only published packs can be shared")
    if not pack.sharing_enabled:
        raise HTTPException(status_code=422, detail="Sharing is not enabled for this pack")
    if body.target_org_id == org_id:
        raise HTTPException(status_code=422, detail="Cannot share a pack with its own org")

    # Verify target org exists
    from app.models.organization import Organization, OrgStatus

    target_org = await db.get(Organization, body.target_org_id)
    if target_org is None or target_org.status == OrgStatus.ARCHIVED:
        raise HTTPException(status_code=404, detail="Target organization not found")

    share = PackShare(
        pack_id=pack_id,
        target_org_id=body.target_org_id,
        shared_by=user.id,
    )
    db.add(share)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Pack already shared with this org") from None
    await db.commit()
    return DataResponse(
        data=PackShareResponse(
            id=share.id,
            pack_id=share.pack_id,
            target_org_id=share.target_org_id,
            shared_by=share.shared_by,
            shared_at=share.shared_at.isoformat() if share.shared_at else "",
        )
    )


@router.get(
    "/orgs/{org_id}/shared-with-me",
    response_model=DataResponse[list[SkillPackResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_shared_packs(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List packs shared with this org (installable even if PRIVATE)."""
    await require_org_member(org_id, user, db)

    result = await db.execute(
        select(SkillPack)
        .join(PackShare, PackShare.pack_id == SkillPack.id)
        .where(
            PackShare.target_org_id == org_id,
            SkillPack.status == PackStatus.PUBLISHED,
        )
        .order_by(SkillPack.name)
    )
    packs = list(result.scalars().all())
    return DataResponse(data=[SkillPackResponse.model_validate(p) for p in packs])


@router.delete(
    "/orgs/{org_id}/packs/{pack_id}/share/{target_org_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def revoke_share(
    org_id: str,
    pack_id: str,
    target_org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a pack share."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)

    result = await db.execute(
        select(PackShare).where(
            PackShare.pack_id == pack_id,
            PackShare.target_org_id == target_org_id,
        )
    )
    share = result.scalar_one_or_none()
    if share is None:
        raise HTTPException(status_code=404, detail="Share not found")

    # Verify the pack belongs to this org (only the owner org can revoke)
    pack = await db.get(SkillPack, pack_id)
    if pack is None or pack.owner_org_id != org_id:
        raise HTTPException(status_code=404, detail="Pack not found")

    await db.delete(share)
    await db.commit()

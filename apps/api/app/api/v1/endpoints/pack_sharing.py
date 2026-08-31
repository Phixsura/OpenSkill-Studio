"""Cross-organization pack sharing endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.skill_pack import PublicSkillPackResponse
from app.services.pack_sharing import PackSharingService

router = APIRouter(tags=["Pack Sharing"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


class SharePackRequest(BaseModel):
    target_org_id: str


class PackShareResponse(BaseModel):
    id: str
    pack_id: str
    target_org_id: str
    shared_by: str
    shared_at: datetime | None = None

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
    svc = PackSharingService(db)
    share = await svc.share_pack(org_id, pack_id, body.target_org_id, user.id)
    await db.commit()
    return DataResponse(data=PackShareResponse.model_validate(share))


@router.get(
    "/orgs/{org_id}/shared-with-me",
    response_model=DataResponse[list[PublicSkillPackResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_shared_packs(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List packs shared with this org (installable even if PRIVATE).

    R92h: the grantee is a DIFFERENT tenant, so serialize via
    PublicSkillPackResponse — the same sanitized shape the anon registry uses
    (R71) — NOT the internal SkillPackResponse. The internal shape leaked the
    owner org's rejection_reason (moderator's private note), review_status,
    owner_org_id and created_by cross-tenant.
    """
    await require_org_member(org_id, user, db)
    svc = PackSharingService(db)
    packs = await svc.list_shared_packs(org_id)
    return DataResponse(data=[PublicSkillPackResponse.model_validate(p) for p in packs])


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
    svc = PackSharingService(db)
    await svc.revoke_share(org_id, pack_id, target_org_id)
    await db.commit()

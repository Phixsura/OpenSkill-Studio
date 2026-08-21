"""Pack installation endpoints — install, list, upgrade, fork, remove."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.skill_pack import SkillPack, SkillPackInstallation
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.services.installation import InstallationService

router = APIRouter(tags=["Installations"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


class InstallRequest(BaseModel):
    pack_id: str
    version: str | None = None  # None = latest


class UpgradeRequest(BaseModel):
    version: str


class InstallResponse(BaseModel):
    id: str
    org_id: str
    pack_id: str | None
    pack_name: str | None = None
    release_id: str | None
    installed_version: str
    status: str
    installed_by: str
    installed_at: datetime

    model_config = {"from_attributes": True}


# ── Helpers ──


async def _enrich_with_pack_name(
    db: AsyncSession, installs: list[SkillPackInstallation],
) -> list[InstallResponse]:
    """Convert installations to InstallResponse with pack_name populated."""
    pack_ids = {i.pack_id for i in installs if i.pack_id}
    name_map: dict[str, str] = {}
    if pack_ids:
        rows = await db.execute(
            select(SkillPack.id, SkillPack.name).where(SkillPack.id.in_(pack_ids))
        )
        name_map = {r[0]: r[1] for r in rows.all()}

    result: list[InstallResponse] = []
    for inst in installs:
        resp = InstallResponse.model_validate(inst)
        resp.pack_name = name_map.get(inst.pack_id) if inst.pack_id else None
        result.append(resp)
    return result


# ── Endpoints ──


@router.post(
    "/orgs/{org_id}/installations",
    response_model=DataResponse[InstallResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(5, 60))],
)
async def install_pack(
    org_id: str,
    body: InstallRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = InstallationService(db)
    inst = await svc.install_pack(org_id, body.pack_id, body.version, user.id)
    await db.commit()
    enriched = await _enrich_with_pack_name(db, [inst])
    return DataResponse(data=enriched[0])


@router.get(
    "/orgs/{org_id}/installations",
    response_model=ListResponse[InstallResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_installations(
    org_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = InstallationService(db)
    installs, total = await svc.list_installations(org_id, page, per_page)
    enriched = await _enrich_with_pack_name(db, installs)
    return ListResponse(
        data=enriched,
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/installations/{install_id}",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_installation(
    org_id: str,
    install_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = InstallationService(db)
    inst = await svc.get_installation(install_id, org_id)
    enriched = await _enrich_with_pack_name(db, [inst])
    inst_data = enriched[0].model_dump()
    update = await svc.check_update(install_id, org_id)
    return DataResponse(data={**inst_data, **update})


@router.get(
    "/orgs/{org_id}/installations/{install_id}/diff",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_diff(
    org_id: str,
    install_id: str,
    version: str = Query(..., description="Target version to diff against"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = InstallationService(db)
    diff = await svc.compute_diff(install_id, org_id, version)
    return DataResponse(data=diff)


@router.post(
    "/orgs/{org_id}/installations/{install_id}/upgrade",
    response_model=DataResponse[InstallResponse],
    dependencies=[Depends(rate_limit(5, 60))],
)
async def upgrade_installation(
    org_id: str,
    install_id: str,
    body: UpgradeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = InstallationService(db)
    inst = await svc.upgrade(install_id, org_id, body.version, user.id)
    await db.commit()
    enriched = await _enrich_with_pack_name(db, [inst])
    return DataResponse(data=enriched[0])


@router.post(
    "/orgs/{org_id}/installations/{install_id}/fork",
    response_model=DataResponse[InstallResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def fork_installation(
    org_id: str,
    install_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = InstallationService(db)
    inst = await svc.fork(install_id, org_id)
    await db.commit()
    enriched = await _enrich_with_pack_name(db, [inst])
    return DataResponse(data=enriched[0])


@router.delete("/orgs/{org_id}/installations/{install_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def remove_installation(
    org_id: str,
    install_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = InstallationService(db)
    await svc.remove(install_id, org_id)
    await db.commit()

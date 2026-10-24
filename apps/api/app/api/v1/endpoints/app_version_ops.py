"""App version operations — rollback, pin, auto-upgrade control."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.developer import AppInstallationResponse
from app.services import developer as dev_svc

router = APIRouter(tags=["App Version Operations"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


class RollbackRequest(BaseModel):
    target_version_id: str


@router.post(
    "/orgs/{org_id}/apps/installations/{installation_id}/rollback",
    response_model=DataResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def rollback_installation(
    org_id: str,
    installation_id: str,
    body: RollbackRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Rollback an installation to a specific previous version."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()

    # Verify target version exists and belongs to the same app
    target_version = await dev_svc.get_app_version(db, body.target_version_id)
    if target_version.app_id != installation.app_id:
        raise dev_svc.AppVersionNotFoundError(
            message="Target version does not belong to this app"
        )

    installation = await dev_svc.update_installation(
        db, installation, app_version_id=body.target_version_id
    )
    await db.commit()
    return DataResponse(data=AppInstallationResponse.model_validate(installation))


@router.post(
    "/orgs/{org_id}/apps/installations/{installation_id}/pin",
    response_model=DataResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def pin_version(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Pin the current version — prevents auto-upgrades."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()

    installation = await dev_svc.update_installation(db, installation, pinned_version=True)
    await db.commit()
    return DataResponse(data=AppInstallationResponse.model_validate(installation))


@router.post(
    "/orgs/{org_id}/apps/installations/{installation_id}/unpin",
    response_model=DataResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def unpin_version(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Unpin version — allows auto-upgrades again."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()

    installation = await dev_svc.update_installation(db, installation, pinned_version=False)
    await db.commit()
    return DataResponse(data=AppInstallationResponse.model_validate(installation))

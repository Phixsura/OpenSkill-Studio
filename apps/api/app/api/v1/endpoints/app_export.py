"""App export endpoints — backup and migration."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.services import developer as dev_svc
from app.services.app_export import export_app_config, export_installation_config

router = APIRouter(tags=["App Export"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


@router.get(
    "/developer/apps/{app_id}/export",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def export_app(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export app configuration for backup/migration (developer only)."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    data = await export_app_config(db, app_id)
    return DataResponse(data=data)


@router.get(
    "/orgs/{org_id}/apps/installations/{installation_id}/export",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def export_installation(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export installation configuration for backup/migration (org admin only)."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()

    data = await export_installation_config(db, installation_id)
    return DataResponse(data=data)

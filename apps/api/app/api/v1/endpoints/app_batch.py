"""Batch operations for developer apps."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse
from app.services import developer as dev_svc
from app.services.app_lifecycle import auto_upgrade_installations

router = APIRouter(tags=["App Batch Operations"])


class BatchUpgradeRequest(BaseModel):
    app_id: str
    version_id: str


@router.post(
    "/developer/apps/{app_id}/batch-upgrade",
    dependencies=[Depends(rate_limit(5, 60))],
)
async def batch_upgrade_installations(
    app_id: str,
    body: BatchUpgradeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upgrade all non-pinned installations to a specific version.

    Only the app owner can trigger batch upgrades.
    """
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    # Verify version exists, belongs to this app, and is approved
    version = await dev_svc.get_app_version(db, body.version_id)
    if version.app_id != app_id:
        raise dev_svc.AppVersionNotFoundError()

    from app.exceptions import AppError

    review_status = version.review_status.value if hasattr(version.review_status, "value") else version.review_status
    if review_status != "APPROVED":
        raise AppError("VERSION_NOT_APPROVED", "Only approved versions can be rolled out", 422)

    app_status = app.status.value if hasattr(app.status, "value") else app.status
    if app_status not in ("PUBLISHED", "DEPRECATED"):
        raise AppError("APP_NOT_PUBLISHED", "App must be published to batch upgrade", 422)

    count = await auto_upgrade_installations(db, app_id, body.version_id)
    await db.commit()

    return DataResponse(
        data={
            "app_id": app_id,
            "version_id": body.version_id,
            "upgraded_count": count,
        }
    )


class CompatibilityCheckRequest(BaseModel):
    current_version_id: str
    new_version_id: str


@router.post(
    "/developer/apps/{app_id}/check-compatibility",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def check_version_compatibility(
    app_id: str,
    body: CompatibilityCheckRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check compatibility between two app versions.

    Reports breaking changes, permission diffs, and upgrade safety.
    """
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    current_ver = await dev_svc.get_app_version(db, body.current_version_id)
    new_ver = await dev_svc.get_app_version(db, body.new_version_id)

    if current_ver.app_id != app_id or new_ver.app_id != app_id:
        raise dev_svc.AppVersionNotFoundError()

    from app.services.app_compatibility import check_upgrade_compatibility

    report = check_upgrade_compatibility(current_ver.manifest, new_ver.manifest)
    return DataResponse(
        data={
            "app_id": app_id,
            "from_version": current_ver.version,
            "to_version": new_ver.version,
            **report,
        }
    )


class DeprecationNoticeRequest(BaseModel):
    message: str | None = None
    sunset_date: str | None = None
    migration_guide_url: str | None = None


@router.post(
    "/developer/apps/{app_id}/deprecation-notice",
    dependencies=[Depends(rate_limit(5, 60))],
)
async def send_deprecation_notice(
    app_id: str,
    body: DeprecationNoticeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a deprecation notice to all active installations.

    The app must be in 'published' or 'deprecated' state.
    """
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    # Count active installations that would be notified
    installations, total = await dev_svc.list_installations(
        db, app_id=app_id, status="active"
    )

    return DataResponse(
        data={
            "app_id": app_id,
            "notice": {
                "message": body.message or "This app is being deprecated.",
                "sunset_date": body.sunset_date,
                "migration_guide_url": body.migration_guide_url,
            },
            "notified_installations": total,
        }
    )

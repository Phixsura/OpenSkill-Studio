"""App lifecycle management — deprecation notices, version pinning, auto-upgrade.

Centralizes lifecycle operations that span multiple service layers.
"""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.developer import (
    AppInstallation,
    AppVersion,
    DeveloperApp,
    InstallationStatus,
)

log = structlog.get_logger()


async def get_deprecation_info(db: AsyncSession, app_id: str) -> dict | None:
    """Get deprecation status for an app.

    Returns None if app is not deprecated, otherwise returns info dict.
    """
    result = await db.execute(
        select(DeveloperApp).where(DeveloperApp.id == app_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        return None

    status = app.status.value if hasattr(app.status, "value") else app.status
    if status != "DEPRECATED":
        return None

    return {
        "app_id": app_id,
        "app_name": app.name,
        "status": "deprecated",
        "message": "This app has been deprecated and will no longer receive updates. Existing installations continue to work.",
        "deprecated_at": app.updated_at.isoformat() if app.updated_at else None,
    }


async def auto_upgrade_installations(
    db: AsyncSession, app_id: str, new_version_id: str
) -> int:
    """Auto-upgrade all non-pinned installations to a new version.

    Returns the number of installations upgraded.
    """
    result = await db.execute(
        update(AppInstallation)
        .where(
            AppInstallation.app_id == app_id,
            AppInstallation.status == InstallationStatus.ACTIVE,
            AppInstallation.pinned_version.is_(False),
        )
        .values(app_version_id=new_version_id)
        .returning(AppInstallation.id)
    )
    upgraded_ids = result.scalars().all()
    count = len(upgraded_ids)

    if count > 0:
        log.info(
            "auto_upgrade_installations",
            app_id=app_id,
            new_version_id=new_version_id,
            count=count,
        )
    return count


async def get_version_adoption(db: AsyncSession, app_id: str) -> list[dict]:
    """Get version adoption statistics — what percentage of installs use each version."""
    from sqlalchemy import func

    result = await db.execute(
        select(
            AppVersion.version,
            AppVersion.id,
            func.count(AppInstallation.id).label("install_count"),
        )
        .outerjoin(
            AppInstallation,
            (AppInstallation.app_version_id == AppVersion.id)
            & (AppInstallation.status == InstallationStatus.ACTIVE),
        )
        .where(AppVersion.app_id == app_id)
        .group_by(AppVersion.id, AppVersion.version)
        .order_by(AppVersion.created_at.desc())
    )
    rows = result.all()
    total = sum(r.install_count for r in rows) or 1  # avoid division by zero

    return [
        {
            "version": r.version,
            "version_id": r.id,
            "install_count": r.install_count,
            "adoption_pct": round((r.install_count / total) * 100, 1),
        }
        for r in rows
    ]


async def check_app_health(db: AsyncSession, app_id: str) -> dict:
    """Aggregate health check for an app — combines multiple signals."""
    from sqlalchemy import func

    from app.models.developer import SandboxExecution, SandboxExecutionStatus

    since = datetime.now(UTC) - timedelta(hours=24)

    # Execution health
    exec_result = await db.execute(
        select(
            func.count().label("total"),
            func.count()
            .filter(
                SandboxExecution.status.in_([
                    SandboxExecutionStatus.FAILED,
                    SandboxExecutionStatus.TIMEOUT,
                ])
            )
            .label("failed"),
        )
        .select_from(SandboxExecution)
        .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
        .where(
            AppInstallation.app_id == app_id,
            SandboxExecution.created_at >= since,
        )
    )
    exec_row = exec_result.one()
    total = exec_row.total or 0
    failed = exec_row.failed or 0
    error_rate = (failed / total * 100) if total > 0 else 0

    # Determine health status
    if total == 0:
        status = "unknown"
        message = "No executions in the last 24 hours"
    elif error_rate > 50:
        status = "critical"
        message = f"Critical error rate: {error_rate:.0f}%"
    elif error_rate > 20:
        status = "degraded"
        message = f"Elevated error rate: {error_rate:.0f}%"
    else:
        status = "healthy"
        message = f"Operating normally ({error_rate:.0f}% error rate)"

    # Version adoption
    adoption = await get_version_adoption(db, app_id)

    return {
        "status": status,
        "message": message,
        "executions_24h": {"total": total, "failed": failed, "error_rate_pct": round(error_rate, 1)},
        "version_adoption": adoption,
    }

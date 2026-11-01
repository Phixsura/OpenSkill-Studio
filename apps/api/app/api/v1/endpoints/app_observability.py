"""App observability endpoints — usage, errors, health dashboards."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.developer import (
    AppApiKey,
    AppInstallation,
    AppVersion,
    InstallationStatus,
    SandboxExecution,
    SandboxExecutionStatus,
)
from app.models.user import User
from app.schemas.base import DataResponse
from app.services import developer as dev_svc

router = APIRouter(tags=["App Observability"])


# ── Developer Dashboard ─────────────────────────────────


@router.get(
    "/developer/apps/{app_id}/stats",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_app_stats(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get app stats — installs, versions, API keys, executions."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    # Active installs
    install_count = (
        await db.execute(
            select(func.count()).where(
                AppInstallation.app_id == app_id,
                AppInstallation.status == InstallationStatus.ACTIVE,
            )
        )
    ).scalar() or 0

    # Total installs (all time)
    total_installs = (
        await db.execute(
            select(func.count()).where(AppInstallation.app_id == app_id)
        )
    ).scalar() or 0

    # Version count
    version_count = (
        await db.execute(
            select(func.count()).where(AppVersion.app_id == app_id)
        )
    ).scalar() or 0

    # API key count
    key_count = (
        await db.execute(
            select(func.count()).where(
                AppApiKey.app_id == app_id,
                AppApiKey.revoked_at.is_(None),
            )
        )
    ).scalar() or 0

    # Sandbox execution stats (last 24h)
    since = datetime.now(UTC) - timedelta(hours=24)
    exec_q = (
        select(
            func.count().label("total"),
            func.count()
            .filter(SandboxExecution.status == SandboxExecutionStatus.COMPLETED)
            .label("completed"),
            func.count()
            .filter(SandboxExecution.status == SandboxExecutionStatus.FAILED)
            .label("failed"),
            func.count()
            .filter(SandboxExecution.status == SandboxExecutionStatus.TIMEOUT)
            .label("timeout"),
            func.avg(SandboxExecution.duration_ms).label("avg_duration_ms"),
            func.max(SandboxExecution.duration_ms).label("max_duration_ms"),
        )
        .select_from(SandboxExecution)
        .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
        .where(
            AppInstallation.app_id == app_id,
            SandboxExecution.created_at >= since,
        )
    )
    exec_result = (await db.execute(exec_q)).one()

    return DataResponse(
        data={
            "app_id": app_id,
            "status": app.status.value if hasattr(app.status, "value") else app.status,
            "active_installs": install_count,
            "total_installs": total_installs,
            "versions": version_count,
            "active_api_keys": key_count,
            "executions_24h": {
                "total": exec_result.total or 0,
                "completed": exec_result.completed or 0,
                "failed": exec_result.failed or 0,
                "timeout": exec_result.timeout or 0,
                "avg_duration_ms": round(exec_result.avg_duration_ms or 0, 1),
                "max_duration_ms": exec_result.max_duration_ms or 0,
            },
        }
    )


@router.get(
    "/developer/apps/{app_id}/installs/breakdown",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_install_breakdown(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get installation breakdown by status."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    result = await db.execute(
        select(
            AppInstallation.status,
            func.count().label("count"),
        )
        .where(AppInstallation.app_id == app_id)
        .group_by(AppInstallation.status)
    )
    breakdown = {
        row.status.value if hasattr(row.status, "value") else row.status: row.count
        for row in result.all()
    }

    return DataResponse(data={"app_id": app_id, "breakdown": breakdown})


@router.get(
    "/developer/apps/{app_id}/version-adoption",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_version_adoption(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get version adoption stats — what % of installs use each version."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    from app.services.app_lifecycle import get_version_adoption as _get_adoption

    adoption = await _get_adoption(db, app_id)
    return DataResponse(data={"app_id": app_id, "versions": adoption})


@router.get(
    "/developer/apps/{app_id}/health",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_app_health(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Aggregate health check — execution error rate + version adoption."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    from app.services.app_lifecycle import check_app_health

    health = await check_app_health(db, app_id)
    return DataResponse(data={"app_id": app_id, **health})


@router.get(
    "/developer/apps/{app_id}/analytics/installs",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_install_analytics(
    app_id: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get daily install/uninstall timeline for the last N days."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    from app.services.app_analytics import get_install_timeline

    timeline = await get_install_timeline(db, app_id, days=min(days, 90))
    return DataResponse(data={"app_id": app_id, "days": days, "timeline": timeline})


@router.get(
    "/developer/apps/{app_id}/analytics/executions",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_execution_analytics(
    app_id: str,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get hourly execution timeline for the last N days."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    from app.services.app_analytics import get_execution_timeline

    timeline = await get_execution_timeline(db, app_id, days=min(days, 30))
    return DataResponse(data={"app_id": app_id, "days": days, "timeline": timeline})


@router.get(
    "/developer/apps/{app_id}/analytics/summary",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_analytics_summary(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get comprehensive summary metrics."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    from app.services.app_analytics import get_app_summary_metrics

    metrics = await get_app_summary_metrics(db, app_id)
    return DataResponse(data={"app_id": app_id, **metrics})


@router.get(
    "/developer/apps/{app_id}/usage",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_app_usage(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get usage metering summary for an app."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    from app.services.app_usage import get_app_usage_summary

    usage = await get_app_usage_summary(db, app_id=app_id)
    return DataResponse(data=usage)


# ── Tenant/Org Dashboard ────────────────────────────────


@router.get(
    "/orgs/{org_id}/apps/stats",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_org_app_stats(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get aggregate app stats for an organization."""
    await require_org_member(org_id, user, db)

    # Count installed apps
    installed_count = (
        await db.execute(
            select(func.count()).where(
                AppInstallation.org_id == org_id,
                AppInstallation.status == InstallationStatus.ACTIVE,
            )
        )
    ).scalar() or 0

    # Execution stats (last 24h)
    since = datetime.now(UTC) - timedelta(hours=24)
    exec_result = (
        await db.execute(
            select(
                func.count().label("total"),
                func.count()
                .filter(SandboxExecution.status == SandboxExecutionStatus.FAILED)
                .label("failed"),
                func.avg(SandboxExecution.duration_ms).label("avg_duration_ms"),
            )
            .select_from(SandboxExecution)
            .join(
                AppInstallation,
                SandboxExecution.installation_id == AppInstallation.id,
            )
            .where(
                AppInstallation.org_id == org_id,
                SandboxExecution.created_at >= since,
            )
        )
    ).one()

    return DataResponse(
        data={
            "org_id": org_id,
            "installed_apps": installed_count,
            "executions_24h": {
                "total": exec_result.total or 0,
                "failed": exec_result.failed or 0,
                "avg_duration_ms": round(exec_result.avg_duration_ms or 0, 1),
            },
        }
    )

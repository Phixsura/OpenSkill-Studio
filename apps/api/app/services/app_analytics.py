"""App analytics service — aggregated metrics for developer dashboards.

Provides time-series data for installs, executions, and API usage.
"""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.developer import (
    AppInstallation,
    AppVersion,
    InstallationStatus,
    SandboxExecution,
    SandboxExecutionStatus,
)

log = structlog.get_logger()


async def get_install_timeline(
    db: AsyncSession, app_id: str, *, days: int = 30
) -> list[dict]:
    """Get daily install/uninstall counts for the last N days."""
    since = datetime.now(UTC) - timedelta(days=days)

    # New installs per day
    result = await db.execute(
        select(
            func.date_trunc("day", AppInstallation.created_at).label("day"),
            func.count().label("installs"),
        )
        .where(
            AppInstallation.app_id == app_id,
            AppInstallation.created_at >= since,
        )
        .group_by("day")
        .order_by("day")
    )
    daily = {
        row.day.date().isoformat(): {"date": row.day.date().isoformat(), "installs": row.installs, "uninstalls": 0}
        for row in result.all()
    }

    # Uninstalls per day
    result = await db.execute(
        select(
            func.date_trunc("day", AppInstallation.uninstalled_at).label("day"),
            func.count().label("uninstalls"),
        )
        .where(
            AppInstallation.app_id == app_id,
            AppInstallation.uninstalled_at >= since,
            AppInstallation.uninstalled_at.isnot(None),
        )
        .group_by("day")
        .order_by("day")
    )
    for row in result.all():
        key = row.day.date().isoformat()
        if key in daily:
            daily[key]["uninstalls"] = row.uninstalls
        else:
            daily[key] = {"date": key, "installs": 0, "uninstalls": row.uninstalls}

    return sorted(daily.values(), key=lambda d: d["date"])


async def get_execution_timeline(
    db: AsyncSession, app_id: str, *, days: int = 7
) -> list[dict]:
    """Get hourly execution counts for the last N days."""
    since = datetime.now(UTC) - timedelta(days=days)

    result = await db.execute(
        select(
            func.date_trunc("hour", SandboxExecution.created_at).label("hour"),
            func.count().label("total"),
            func.count()
            .filter(SandboxExecution.status == SandboxExecutionStatus.COMPLETED)
            .label("completed"),
            func.count()
            .filter(
                SandboxExecution.status.in_([
                    SandboxExecutionStatus.FAILED,
                    SandboxExecutionStatus.TIMEOUT,
                ])
            )
            .label("failed"),
            func.avg(SandboxExecution.duration_ms).label("avg_ms"),
        )
        .select_from(SandboxExecution)
        .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
        .where(
            AppInstallation.app_id == app_id,
            SandboxExecution.created_at >= since,
        )
        .group_by("hour")
        .order_by("hour")
    )

    return [
        {
            "hour": row.hour.isoformat(),
            "total": row.total,
            "completed": row.completed,
            "failed": row.failed,
            "avg_ms": round(row.avg_ms or 0, 1),
        }
        for row in result.all()
    ]


async def get_top_orgs(
    db: AsyncSession, app_id: str, *, limit: int = 10
) -> list[dict]:
    """Get top organizations by execution count."""
    from app.models.organization import Organization

    result = await db.execute(
        select(
            AppInstallation.org_id,
            Organization.name,
            func.count(SandboxExecution.id).label("execution_count"),
        )
        .select_from(SandboxExecution)
        .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
        .join(Organization, AppInstallation.org_id == Organization.id)
        .where(AppInstallation.app_id == app_id)
        .group_by(AppInstallation.org_id, Organization.name)
        .order_by(func.count(SandboxExecution.id).desc())
        .limit(limit)
    )

    return [
        {"org_id": row.org_id, "org_name": row.name, "execution_count": row.execution_count}
        for row in result.all()
    ]


async def get_app_summary_metrics(db: AsyncSession, app_id: str) -> dict:
    """Comprehensive summary metrics for developer dashboard."""
    now = datetime.now(UTC)
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)
    now - timedelta(days=30)

    # Active installs
    active_installs = (
        await db.execute(
            select(func.count()).where(
                AppInstallation.app_id == app_id,
                AppInstallation.status == InstallationStatus.ACTIVE,
            )
        )
    ).scalar() or 0

    # Installs this week
    week_installs = (
        await db.execute(
            select(func.count()).where(
                AppInstallation.app_id == app_id,
                AppInstallation.created_at >= week_ago,
            )
        )
    ).scalar() or 0

    # Versions count
    version_count = (
        await db.execute(
            select(func.count()).where(AppVersion.app_id == app_id)
        )
    ).scalar() or 0

    # Executions 24h
    exec_24h = (
        await db.execute(
            select(func.count())
            .select_from(SandboxExecution)
            .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
            .where(
                AppInstallation.app_id == app_id,
                SandboxExecution.created_at >= day_ago,
            )
        )
    ).scalar() or 0

    # Executions this week
    exec_week = (
        await db.execute(
            select(func.count())
            .select_from(SandboxExecution)
            .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
            .where(
                AppInstallation.app_id == app_id,
                SandboxExecution.created_at >= week_ago,
            )
        )
    ).scalar() or 0

    return {
        "active_installs": active_installs,
        "installs_this_week": week_installs,
        "versions": version_count,
        "executions_24h": exec_24h,
        "executions_this_week": exec_week,
    }

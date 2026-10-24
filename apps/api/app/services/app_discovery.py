"""App discovery service — featured apps, trending, and recommendations.

Provides curated and algorithmic app discovery for the marketplace.
"""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.developer import (
    AppInstallation,
    AppStatus,
    AppVisibility,
    DeveloperAccount,
    DeveloperApp,
    InstallationStatus,
)

log = structlog.get_logger()


async def get_featured_apps(
    db: AsyncSession, *, limit: int = 6
) -> list[dict]:
    """Get featured apps — highest install count among published public apps."""
    install_count = (
        select(func.count())
        .where(
            AppInstallation.app_id == DeveloperApp.id,
            AppInstallation.status == InstallationStatus.ACTIVE,
        )
        .correlate(DeveloperApp)
        .scalar_subquery()
    )

    result = await db.execute(
        select(DeveloperApp, install_count.label("installs"))
        .where(
            DeveloperApp.status == AppStatus.PUBLISHED,
            DeveloperApp.visibility == AppVisibility.PUBLIC,
        )
        .order_by(install_count.desc(), DeveloperApp.created_at.desc())
        .limit(limit)
    )

    apps = []
    for row in result.all():
        app = row[0]
        installs = row[1] or 0
        dev = await db.execute(
            select(DeveloperAccount.display_name).where(
                DeveloperAccount.id == app.developer_id
            )
        )
        dev_name = dev.scalar_one_or_none()
        apps.append({
            "id": app.id,
            "name": app.name,
            "slug": app.slug,
            "description": app.description,
            "icon_url": app.icon_url,
            "category": app.category.value if hasattr(app.category, "value") else app.category,
            "developer_name": dev_name,
            "install_count": installs,
        })
    return apps


async def get_recent_apps(
    db: AsyncSession, *, limit: int = 10
) -> list[dict]:
    """Get recently published apps."""
    result = await db.execute(
        select(DeveloperApp)
        .where(
            DeveloperApp.status == AppStatus.PUBLISHED,
            DeveloperApp.visibility == AppVisibility.PUBLIC,
        )
        .order_by(DeveloperApp.created_at.desc())
        .limit(limit)
    )
    apps = []
    for app in result.scalars().all():
        dev = await db.execute(
            select(DeveloperAccount.display_name).where(
                DeveloperAccount.id == app.developer_id
            )
        )
        apps.append({
            "id": app.id,
            "name": app.name,
            "slug": app.slug,
            "description": app.description,
            "category": app.category.value if hasattr(app.category, "value") else app.category,
            "developer_name": dev.scalar_one_or_none(),
            "created_at": app.created_at.isoformat() if app.created_at else None,
        })
    return apps


async def get_trending_apps(
    db: AsyncSession, *, days: int = 7, limit: int = 10
) -> list[dict]:
    """Get trending apps — most installations in the last N days."""
    since = datetime.now(UTC) - timedelta(days=days)

    result = await db.execute(
        select(
            DeveloperApp.id,
            DeveloperApp.name,
            DeveloperApp.slug,
            DeveloperApp.category,
            func.count(AppInstallation.id).label("recent_installs"),
        )
        .join(AppInstallation, AppInstallation.app_id == DeveloperApp.id)
        .where(
            DeveloperApp.status == AppStatus.PUBLISHED,
            DeveloperApp.visibility == AppVisibility.PUBLIC,
            AppInstallation.created_at >= since,
        )
        .group_by(DeveloperApp.id, DeveloperApp.name, DeveloperApp.slug, DeveloperApp.category)
        .order_by(func.count(AppInstallation.id).desc())
        .limit(limit)
    )

    return [
        {
            "id": row.id,
            "name": row.name,
            "slug": row.slug,
            "category": row.category.value if hasattr(row.category, "value") else row.category,
            "recent_installs": row.recent_installs,
        }
        for row in result.all()
    ]

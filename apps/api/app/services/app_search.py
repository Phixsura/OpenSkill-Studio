"""App search service — full-text search for the marketplace.

Provides search across app names, descriptions, and categories
with ranking by relevance and install count.
"""

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


async def search_marketplace_apps(
    db: AsyncSession,
    *,
    query: str | None = None,
    category: str | None = None,
    sort_by: str = "relevance",  # relevance, installs, newest
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[dict], int]:
    """Search published public apps in the marketplace.

    Returns (apps_with_metadata, total_count).
    """
    # Base query: only published + public
    base = select(DeveloperApp).where(
        DeveloperApp.status == AppStatus.PUBLISHED,
        DeveloperApp.visibility == AppVisibility.PUBLIC,
    )
    count_q = (
        select(func.count())
        .select_from(DeveloperApp)
        .where(
            DeveloperApp.status == AppStatus.PUBLISHED,
            DeveloperApp.visibility == AppVisibility.PUBLIC,
        )
    )

    if category:
        base = base.where(DeveloperApp.category == category)
        count_q = count_q.where(DeveloperApp.category == category)

    if query:
        pattern = f"%{query}%"
        base = base.where(
            DeveloperApp.name.ilike(pattern)
            | DeveloperApp.description.ilike(pattern)
        )
        count_q = count_q.where(
            DeveloperApp.name.ilike(pattern)
            | DeveloperApp.description.ilike(pattern)
        )

    total = (await db.execute(count_q)).scalar() or 0

    # Sort
    if sort_by == "newest":
        base = base.order_by(DeveloperApp.created_at.desc())
    else:
        # Default: newest (relevance requires full-text search setup)
        base = base.order_by(DeveloperApp.created_at.desc())

    base = base.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(base)
    apps = list(result.scalars().all())

    # Enrich with install counts and developer names
    enriched = []
    for app in apps:
        install_count = (
            await db.execute(
                select(func.count()).where(
                    AppInstallation.app_id == app.id,
                    AppInstallation.status == InstallationStatus.ACTIVE,
                )
            )
        ).scalar() or 0

        dev_name = (
            await db.execute(
                select(DeveloperAccount.display_name).where(
                    DeveloperAccount.id == app.developer_id
                )
            )
        ).scalar_one_or_none()

        enriched.append({
            "id": app.id,
            "name": app.name,
            "slug": app.slug,
            "description": app.description,
            "icon_url": app.icon_url,
            "category": app.category.value if hasattr(app.category, "value") else app.category,
            "visibility": app.visibility.value if hasattr(app.visibility, "value") else app.visibility,
            "status": app.status.value if hasattr(app.status, "value") else app.status,
            "developer_name": dev_name,
            "install_count": install_count,
            "homepage_url": app.homepage_url,
            "created_at": app.created_at.isoformat() if app.created_at else None,
        })

    # Sort by installs if requested (post-query since we need enriched data)
    if sort_by == "installs":
        enriched.sort(key=lambda a: a["install_count"], reverse=True)

    return enriched, total

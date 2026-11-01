"""Public App Marketplace — browse and discover published apps."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limit import rate_limit
from app.models.developer import (
    AppInstallation,
    AppStatus,
    AppVisibility,
    DeveloperAccount,
    DeveloperApp,
    InstallationStatus,
)
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.developer import AppResponse, AppSummaryResponse

router = APIRouter(tags=["App Marketplace"])


@router.get(
    "/marketplace/apps",
    response_model=ListResponse[AppSummaryResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def browse_apps(
    category: str | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Browse published apps in the marketplace (public, no auth required)."""
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

    if q:
        pattern = f"%{q}%"
        base = base.where(
            DeveloperApp.name.ilike(pattern) | DeveloperApp.description.ilike(pattern)
        )
        count_q = count_q.where(
            DeveloperApp.name.ilike(pattern) | DeveloperApp.description.ilike(pattern)
        )

    total = (await db.execute(count_q)).scalar() or 0

    query = (
        base.order_by(DeveloperApp.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    apps = list(result.scalars().all())

    summaries = []
    for app in apps:
        count_result = await db.execute(
            select(func.count()).where(
                AppInstallation.app_id == app.id,
                AppInstallation.status == InstallationStatus.ACTIVE,
            )
        )
        install_count = count_result.scalar() or 0

        dev_result = await db.execute(
            select(DeveloperAccount.display_name).where(
                DeveloperAccount.id == app.developer_id
            )
        )
        dev_name = dev_result.scalar_one_or_none()

        summaries.append(
            AppSummaryResponse(
                id=app.id,
                name=app.name,
                slug=app.slug,
                description=app.description,
                icon_url=app.icon_url,
                category=app.category.value if hasattr(app.category, "value") else app.category,
                visibility=app.visibility.value if hasattr(app.visibility, "value") else app.visibility,
                status=app.status.value if hasattr(app.status, "value") else app.status,
                developer_name=dev_name,
                install_count=install_count,
            )
        )

    return ListResponse(
        data=summaries,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get(
    "/marketplace/apps/{app_id}",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_marketplace_app(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a published app's details (public)."""
    result = await db.execute(
        select(DeveloperApp).where(
            DeveloperApp.id == app_id,
            DeveloperApp.status.in_([AppStatus.PUBLISHED, AppStatus.DEPRECATED]),
            DeveloperApp.visibility.in_([AppVisibility.PUBLIC, AppVisibility.UNLISTED]),
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        from app.services.developer import AppNotFoundError

        raise AppNotFoundError()
    return DataResponse(data=AppResponse.model_validate(app))

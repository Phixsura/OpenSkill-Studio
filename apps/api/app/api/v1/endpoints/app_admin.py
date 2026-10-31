"""Platform admin endpoints for developer platform management."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.core.rate_limit import rate_limit
from app.models.developer import (
    AppInstallation,
    DeveloperAccount,
    DeveloperApp,
    InstallationStatus,
    SandboxExecution,
    SandboxExecutionStatus,
)
from app.models.user import User, UserRole
from app.schemas.base import DataResponse
from app.services import developer as dev_svc

router = APIRouter(tags=["Platform Admin - Apps"])


@router.get(
    "/admin/developer-platform/stats",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_platform_app_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Platform-wide developer platform statistics."""
    # Developer accounts
    dev_count = (
        await db.execute(select(func.count()).select_from(DeveloperAccount))
    ).scalar() or 0

    # Apps by status
    app_status_q = await db.execute(
        select(DeveloperApp.status, func.count().label("count"))
        .group_by(DeveloperApp.status)
    )
    app_by_status = {
        row.status.value if hasattr(row.status, "value") else row.status: row.count
        for row in app_status_q.all()
    }

    # Total apps
    total_apps = sum(app_by_status.values())

    # Active installations
    active_installs = (
        await db.execute(
            select(func.count()).where(
                AppInstallation.status == InstallationStatus.ACTIVE
            )
        )
    ).scalar() or 0

    # Sandbox executions (last 24h)
    from datetime import UTC, datetime, timedelta

    since = datetime.now(UTC) - timedelta(hours=24)
    exec_total = (
        await db.execute(
            select(func.count()).where(SandboxExecution.created_at >= since)
        )
    ).scalar() or 0
    exec_failed = (
        await db.execute(
            select(func.count()).where(
                SandboxExecution.created_at >= since,
                SandboxExecution.status.in_([
                    SandboxExecutionStatus.FAILED,
                    SandboxExecutionStatus.TIMEOUT,
                ]),
            )
        )
    ).scalar() or 0

    return DataResponse(
        data={
            "developer_accounts": dev_count,
            "total_apps": total_apps,
            "apps_by_status": app_by_status,
            "active_installations": active_installs,
            "executions_24h": {
                "total": exec_total,
                "failed": exec_failed,
                "error_rate_pct": round(
                    (exec_failed / exec_total * 100) if exec_total > 0 else 0, 1
                ),
            },
        }
    )


@router.get(
    "/admin/developer-platform/apps",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_all_apps(
    status: str | None = None,
    category: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    """List all apps across all developers (admin only)."""
    apps, total = await dev_svc.list_apps(
        db, category=category, status=status, page=page, per_page=per_page
    )
    from app.schemas.base import ListResponse, PaginationMeta
    from app.schemas.developer import AppSummaryResponse

    return ListResponse(
        data=[AppSummaryResponse.model_validate(a) for a in apps],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


class AdminRevokeRequest(BaseModel):
    reason: str


@router.post(
    "/admin/developer-platform/apps/{app_id}/revoke",
    dependencies=[Depends(rate_limit(5, 60))],
)
async def admin_revoke_app(
    app_id: str,
    body: AdminRevokeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Admin emergency revoke — suspends app and all installations."""
    app = await dev_svc.revoke_app(db, app_id, reason=body.reason)
    await db.commit()
    from app.schemas.developer import AppResponse

    return DataResponse(data=AppResponse.model_validate(app))


@router.get(
    "/admin/developer-platform/developers",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_all_developers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    """List all developer accounts (admin only)."""
    accounts, total = await dev_svc.list_developer_accounts(db, page=page, per_page=per_page)
    from app.schemas.base import ListResponse, PaginationMeta
    from app.schemas.developer import DeveloperAccountResponse

    return ListResponse(
        data=[DeveloperAccountResponse.model_validate(a) for a in accounts],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )

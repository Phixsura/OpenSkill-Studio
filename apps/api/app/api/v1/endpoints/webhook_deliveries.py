"""Webhook delivery log endpoints — track delivery status for app developers."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.models.webhook_delivery import AppWebhookDelivery
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.services import developer as dev_svc

router = APIRouter(tags=["Webhook Deliveries"])


@router.get(
    "/developer/apps/{app_id}/webhook-deliveries",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_webhook_deliveries(
    app_id: str,
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List webhook delivery history for an app (developer only)."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    q = select(AppWebhookDelivery).where(AppWebhookDelivery.app_id == app_id)
    count_q = (
        select(func.count())
        .select_from(AppWebhookDelivery)
        .where(AppWebhookDelivery.app_id == app_id)
    )

    if status:
        q = q.where(AppWebhookDelivery.status == status)
        count_q = count_q.where(AppWebhookDelivery.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    q = q.order_by(AppWebhookDelivery.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    deliveries = result.scalars().all()

    return ListResponse(
        data=[
            {
                "id": d.id,
                "event_type": d.event_type,
                "event_id": d.event_id,
                "url": d.url,
                "status": d.status.value if hasattr(d.status, "value") else d.status,
                "http_status": d.http_status,
                "attempt": d.attempt,
                "max_attempts": d.max_attempts,
                "error_message": d.error_message,
                "duration_ms": d.duration_ms,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
            }
            for d in deliveries
        ],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get(
    "/developer/apps/{app_id}/webhook-deliveries/stats",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_webhook_delivery_stats(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get webhook delivery stats for an app."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    result = await db.execute(
        select(
            AppWebhookDelivery.status,
            func.count().label("count"),
        )
        .where(AppWebhookDelivery.app_id == app_id)
        .group_by(AppWebhookDelivery.status)
    )
    breakdown = {
        row.status.value if hasattr(row.status, "value") else row.status: row.count
        for row in result.all()
    }

    # Average delivery time
    avg_result = await db.execute(
        select(func.avg(AppWebhookDelivery.duration_ms)).where(
            AppWebhookDelivery.app_id == app_id,
            AppWebhookDelivery.duration_ms.isnot(None),
        )
    )
    avg_duration = avg_result.scalar() or 0

    return DataResponse(
        data={
            "app_id": app_id,
            "delivery_breakdown": breakdown,
            "avg_duration_ms": round(avg_duration, 1),
            "total": sum(breakdown.values()),
        }
    )

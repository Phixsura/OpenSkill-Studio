"""Usage endpoints: manual ingestion, tenant aggregates, platform explorer,
adjustments (ADR-014 §3.4)."""

from datetime import UTC, datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.usage import USAGE_TYPES, UsageEvent
from app.controlplane.services import metering
from app.controlplane.services import tenants as tenant_svc
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import (
    DataResponse,
    ListResponse,
    PaginationMeta,
    reject_ctrl_json,
    reject_deep_json,
)

log = structlog.get_logger()

router = APIRouter(tags=["Usage"])


class IngestUsageRequest(BaseModel):
    usage_type: str
    quantity: str | int | float
    occurred_at: datetime
    idempotency_key: str = Field(min_length=8, max_length=120)
    provider: str | None = Field(default=None, max_length=50)
    model_or_service: str | None = Field(default=None, max_length=200)
    project_id: str | None = Field(default=None, min_length=26, max_length=26)
    metadata: dict = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def _meta(cls, v):
        reject_deep_json(v, "metadata", limit=8)
        reject_ctrl_json(v, "metadata")
        return v


class AdjustUsageRequest(BaseModel):
    delta_quantity: str | int | float
    reason: str = Field(min_length=3, max_length=500)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=120)


class UsageEventResponse(BaseModel):
    id: str
    tenant_id: str
    org_id: str
    usage_type: str
    quantity: str
    unit: str
    occurred_at: datetime
    source: str
    provider: str | None
    model_or_service: str | None
    workflow_run_id: str | None
    evaluation_task_id: str | None
    adjustment_of_id: str | None
    metadata: dict
    created_at: datetime

    @classmethod
    def from_row(cls, e: UsageEvent) -> "UsageEventResponse":
        return cls(
            id=e.id,
            tenant_id=e.tenant_id,
            org_id=e.org_id,
            usage_type=e.usage_type,
            quantity=str(e.quantity),
            unit=e.unit,
            occurred_at=e.occurred_at,
            source=e.source,
            provider=e.provider,
            model_or_service=e.model_or_service,
            workflow_run_id=e.workflow_run_id,
            evaluation_task_id=e.evaluation_task_id,
            adjustment_of_id=e.adjustment_of_id,
            metadata=e.metadata_ or {},
            created_at=e.created_at,
        )


@router.post(
    "/orgs/{org_id}/usage-events",
    status_code=201,
    dependencies=[Depends(rate_limit(30, 60))],
)
async def ingest_usage(
    org_id: str,
    body: IngestUsageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """External/manual ingestion. tenant/org derived from the PATH — the body
    cannot plant foreign attribution. Source is forced to 'manual'."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    from app.controlplane import facade

    tenant = await facade.get_tenant_for_org(db, org_id)
    facade.require_tenant_active(tenant)
    await facade.require_feature(db, tenant, "api_access")
    if body.occurred_at > datetime.now(UTC) + timedelta(minutes=5):
        raise AppError("INVALID_QUANTITY", "occurred_at cannot be in the future", 422)
    event = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id=org_id,
        usage_type=body.usage_type,
        quantity=body.quantity,
        occurred_at=body.occurred_at,
        source="manual",
        idempotency_key=body.idempotency_key,
        user_id=user.id,
        project_id=body.project_id,
        provider=body.provider,
        model_or_service=body.model_or_service,
        metadata=body.metadata,
    )
    if event is None:
        # Duplicate — return the original (200 semantics via payload flag)
        existing = (
            await db.execute(
                select(UsageEvent).where(UsageEvent.idempotency_key == body.idempotency_key)
            )
        ).scalar_one()
        return DataResponse(
            data={**UsageEventResponse.from_row(existing).model_dump(), "duplicate": True}
        )
    await db.commit()
    return DataResponse(data=UsageEventResponse.from_row(event).model_dump())


@router.get(
    "/tenants/{tenant_id}/usage",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def tenant_usage_aggregate(
    tenant_id: str,
    period: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    org_id: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    query = (
        select(
            UsageEvent.usage_type,
            UsageEvent.unit,
            func.sum(UsageEvent.quantity).label("quantity"),
            func.count(UsageEvent.id).label("event_count"),
        )
        .where(UsageEvent.tenant_id == tenant_id)
        .group_by(UsageEvent.usage_type, UsageEvent.unit)
        .order_by(UsageEvent.usage_type)
    )
    if org_id:
        query = query.where(UsageEvent.org_id == org_id)
    if period:
        # Month bounds in the tenant's timezone (ADR-014 §3.4)
        from zoneinfo import ZoneInfo

        tenant = await db.get(tenant_svc.TenantAccount, tenant_id)
        try:
            tz = ZoneInfo(tenant.timezone)
        except Exception:  # noqa: BLE001 — bad tz falls back to UTC
            tz = UTC
        year, month = int(period[:4]), int(period[5:7])
        start = datetime(year, month, 1, tzinfo=tz)
        end = datetime(year + (month == 12), (month % 12) + 1, 1, tzinfo=tz)
        query = query.where(UsageEvent.occurred_at >= start, UsageEvent.occurred_at < end)
    rows = (await db.execute(query)).all()
    return DataResponse(
        data={
            "period": period,
            "usage": [
                {
                    "usage_type": r.usage_type,
                    "unit": r.unit,
                    "quantity": str(r.quantity),
                    "event_count": r.event_count,
                }
                for r in rows
            ],
        }
    )


@router.get(
    "/platform/usage-events",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def platform_usage_explorer(
    tenant_id: str | None = Query(default=None),
    org_id: str | None = Query(default=None),
    usage_type: str | None = Query(default=None),
    source: str | None = Query(default=None),
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(require_platform_role("platform_admin", "billing_admin")),
    db: AsyncSession = Depends(get_db),
):
    query = select(UsageEvent)
    if tenant_id:
        query = query.where(UsageEvent.tenant_id == tenant_id)
    if org_id:
        query = query.where(UsageEvent.org_id == org_id)
    if usage_type:
        if usage_type not in USAGE_TYPES:
            raise AppError("UNKNOWN_USAGE_TYPE", f"Unknown usage type '{usage_type}'", 422)
        query = query.where(UsageEvent.usage_type == usage_type)
    if source:
        query = query.where(UsageEvent.source == source)
    if from_:
        query = query.where(UsageEvent.occurred_at >= from_)
    if to:
        query = query.where(UsageEvent.occurred_at < to)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                query.order_by(UsageEvent.occurred_at.desc()).offset(offset).limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[UsageEventResponse.from_row(e).model_dump() for e in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.post(
    "/platform/usage-events/{event_id}/adjust",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def adjust_usage(
    event_id: str,
    body: AdjustUsageRequest,
    request: Request,
    user: User = Depends(require_platform_role("billing_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    event = await metering.ingest_adjustment(
        db,
        original_event_id=event_id,
        delta_quantity=body.delta_quantity,
        reason=body.reason,
        actor=make_actor(request, user),
        idempotency_key=body.idempotency_key,
    )
    await db.commit()
    return DataResponse(data=UsageEventResponse.from_row(event).model_dump())

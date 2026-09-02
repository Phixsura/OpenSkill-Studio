"""Pricing endpoints: cost rates, price policies, FX, rated usage,
reconciliation (ADR-014 §4.6). Cost/margin data NEVER leaves platform scope."""

from datetime import UTC, datetime
from decimal import Decimal

import structlog
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.pricing import (
    FxRate,
    PricePolicy,
    ProviderCostRate,
    RatedUsage,
    ReconciliationReport,
)
from app.controlplane.models.usage import UsageEvent
from app.controlplane.services import pricing as pricing_svc
from app.controlplane.services import rating as rating_svc
from app.controlplane.services import tenants as tenant_svc
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import (
    DataResponse,
    ListResponse,
    PaginationMeta,
    reject_ctrl_str,
    reject_deep_json,
    safe_decimal,
)

log = structlog.get_logger()

router = APIRouter(tags=["Pricing & Rating"])

_BILLING_ROLES = ("billing_admin", "platform_admin")


# ── Schemas ──────────────────────────────────────────────────


class CreateCostRateRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    model_or_service: str | None = Field(default=None, max_length=200)
    usage_type: str
    capability_key: str | None = Field(default=None, max_length=64)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    unit_cost: str  # decimal string
    tier_rules: list[dict] | None = Field(default=None, max_length=20)
    minimum_fee_minor: int | None = Field(default=None, ge=0, le=1_000_000_000_000_000)
    effective_from: datetime
    effective_until: datetime | None = None
    source_note: str | None = Field(default=None, max_length=500)

    @field_validator("source_note", "provider")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)

    @field_validator("unit_cost")
    @classmethod
    def _cost(cls, v, info):
        d = safe_decimal(v, info.field_name)
        # Column is Numeric(18,8): integer part must be < 10^10, else the
        # INSERT overflows PG (R88 class → 500). Bound at the schema.
        if not d.is_finite() or d < 0 or d >= Decimal("10000000000"):
            raise ValueError("unit_cost must be non-negative and < 10^10")
        return v

    @field_validator("tier_rules")
    @classmethod
    def _tiers(cls, v):
        if v is None:
            return v
        reject_deep_json(v, "tier_rules", limit=3)
        for tier in v:
            safe_decimal(str(tier.get("min_qty", "0")), "tier_rules.min_qty")
            safe_decimal(str(tier.get("unit_cost")), "tier_rules.unit_cost")
        return v


class SupersedeCostRateRequest(BaseModel):
    effective_until: datetime
    successor: CreateCostRateRequest


class CreatePricePolicyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    policy_type: str
    usage_type: str | None = None
    capability_key: str | None = Field(default=None, max_length=64)
    plan_version_id: str | None = Field(default=None, min_length=26, max_length=26)
    tenant_id: str | None = Field(default=None, min_length=26, max_length=26)
    partner_id: str | None = Field(default=None, min_length=26, max_length=26)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    params: dict
    priority: int = Field(default=0, ge=-1000, le=1000)
    effective_from: datetime
    effective_until: datetime | None = None

    @field_validator("name")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)

    @field_validator("params")
    @classmethod
    def _params(cls, v):
        reject_deep_json(v, "params", limit=3)
        return v


class CreateFxRateRequest(BaseModel):
    base_currency: str = Field(pattern=r"^[A-Z]{3}$")
    quote_currency: str = Field(pattern=r"^[A-Z]{3}$")
    rate: str
    effective_from: datetime
    effective_until: datetime | None = None

    @field_validator("rate")
    @classmethod
    def _rate(cls, v, info):
        # Numeric(18,8): integer part < 10^10 or the INSERT overflows → 500.
        d = safe_decimal(v, info.field_name)
        if not d.is_finite() or d <= 0 or d >= Decimal("10000000000"):
            raise ValueError("rate must be positive and < 10^10")
        return v


class CreateReconReportRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    model_or_service: str | None = Field(default=None, max_length=200)
    usage_type: str
    period: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    provider_reported_quantity: str
    provider_reported_cost_minor: int = Field(ge=0, le=1_000_000_000_000_000)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    note: str | None = Field(default=None, max_length=500)

    @field_validator("note", "provider")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)

    @field_validator("provider_reported_quantity")
    @classmethod
    def _qty(cls, v, info):
        # Numeric(18,6): raw string is fed straight to Decimal() in the
        # handler — a NaN/Infinity or over-range value would 500 the write.
        d = safe_decimal(v, info.field_name)
        if not d.is_finite() or d < 0 or d >= Decimal("1000000000000"):
            raise ValueError("quantity must be non-negative and < 10^12")
        return v


class VoidRatedRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


def _cost_rate_response(r: ProviderCostRate) -> dict:
    return {
        "id": r.id,
        "provider": r.provider,
        "model_or_service": r.model_or_service,
        "usage_type": r.usage_type,
        "capability_key": r.capability_key,
        "unit": r.unit,
        "currency": r.currency,
        "unit_cost": str(r.unit_cost),
        "tier_rules": r.tier_rules,
        "minimum_fee_minor": r.minimum_fee_minor,
        "effective_from": r.effective_from.isoformat(),
        "effective_until": r.effective_until.isoformat() if r.effective_until else None,
        "source_note": r.source_note,
    }


def _policy_response(p: PricePolicy) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "policy_type": p.policy_type,
        "usage_type": p.usage_type,
        "capability_key": p.capability_key,
        "plan_version_id": p.plan_version_id,
        "tenant_id": p.tenant_id,
        "partner_id": p.partner_id,
        "currency": p.currency,
        "params": p.params,
        "priority": p.priority,
        "effective_from": p.effective_from.isoformat(),
        "effective_until": p.effective_until.isoformat() if p.effective_until else None,
        "is_active": p.is_active,
    }


def _platform_rated_response(r: RatedUsage) -> dict:
    """FULL fields — platform roles only."""
    return {
        "id": r.id,
        "usage_event_id": r.usage_event_id,
        "tenant_id": r.tenant_id,
        "org_id": r.org_id,
        "usage_type": r.usage_type,
        "quantity": str(r.quantity),
        "cost_rate_snapshot": r.cost_rate_snapshot,
        "internal_cost_minor": r.internal_cost_minor,
        "internal_cost_currency": r.internal_cost_currency,
        "sell_rate_snapshot": r.sell_rate_snapshot,
        "billable_amount_minor": r.billable_amount_minor,
        "billable_currency": r.billable_currency,
        "fx_rate_snapshot": r.fx_rate_snapshot,
        "margin_minor": r.margin_minor,
        "status": r.status,
        "invoice_line_id": r.invoice_line_id,
        "rated_at": r.rated_at.isoformat(),
    }


def _tenant_rated_response(r: RatedUsage) -> dict:
    """WHITELIST — billable side only. Never cost/margin/fx (R82 rule).
    Field set asserted in tests against TENANT_RATED_FIELDS."""
    return {
        "id": r.id,
        "usage_event_id": r.usage_event_id,
        "usage_type": r.usage_type,
        "quantity": str(r.quantity),
        "billable_amount_minor": r.billable_amount_minor,
        "billable_currency": r.billable_currency,
        "status": r.status,
        "rated_at": r.rated_at.isoformat(),
    }


TENANT_RATED_FIELDS = frozenset(
    {
        "id",
        "usage_event_id",
        "usage_type",
        "quantity",
        "billable_amount_minor",
        "billable_currency",
        "status",
        "rated_at",
    }
)


# ── Cost rates ───────────────────────────────────────────────


@router.get("/platform/cost-rates", dependencies=[Depends(rate_limit(30, 60))])
async def list_cost_rates(
    provider: str | None = Query(default=None),
    usage_type: str | None = Query(default=None),
    at: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    q = select(ProviderCostRate)
    if provider:
        q = q.where(ProviderCostRate.provider == provider)
    if usage_type:
        q = q.where(ProviderCostRate.usage_type == usage_type)
    if at:
        from sqlalchemy import or_ as _or

        q = q.where(
            ProviderCostRate.effective_from <= at,
            _or(
                ProviderCostRate.effective_until.is_(None),
                ProviderCostRate.effective_until > at,
            ),
        )
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(ProviderCostRate.effective_from.desc(), ProviderCostRate.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_cost_rate_response(r) for r in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.post("/platform/cost-rates", status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def create_cost_rate(
    body: CreateCostRateRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    rate = await pricing_svc.create_cost_rate(
        db,
        actor=make_actor(request, user),
        provider=body.provider,
        model_or_service=body.model_or_service,
        usage_type=body.usage_type,
        capability_key=body.capability_key,
        currency=body.currency,
        unit_cost=Decimal(body.unit_cost),
        tier_rules=body.tier_rules,
        minimum_fee_minor=body.minimum_fee_minor,
        effective_from=body.effective_from,
        effective_until=body.effective_until,
        source_note=body.source_note,
    )
    await db.commit()
    return DataResponse(data=_cost_rate_response(rate))


@router.post(
    "/platform/cost-rates/{rate_id}/supersede",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def supersede_cost_rate(
    rate_id: str,
    body: SupersedeCostRateRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    rate = await db.get(ProviderCostRate, rate_id)
    if rate is None:
        raise AppError("RATING_NOT_FOUND", "Cost rate not found", 404)
    successor_fields = body.successor.model_dump(exclude_none=True)
    if "unit_cost" in successor_fields:
        successor_fields["unit_cost"] = Decimal(successor_fields["unit_cost"])
    new_rate = await pricing_svc.supersede_cost_rate(
        db,
        rate,
        effective_until=body.effective_until,
        successor=successor_fields,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(data=_cost_rate_response(new_rate))


# ── Price policies ───────────────────────────────────────────


@router.get("/platform/price-policies", dependencies=[Depends(rate_limit(30, 60))])
async def list_price_policies(
    tenant_id: str | None = Query(default=None),
    usage_type: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    q = select(PricePolicy)
    if tenant_id:
        q = q.where(PricePolicy.tenant_id == tenant_id)
    if usage_type:
        q = q.where(PricePolicy.usage_type == usage_type)
    if active_only:
        q = q.where(PricePolicy.is_active.is_(True))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(PricePolicy.effective_from.desc(), PricePolicy.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_policy_response(p) for p in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.post(
    "/platform/price-policies", status_code=201, dependencies=[Depends(rate_limit(20, 60))]
)
async def create_price_policy(
    body: CreatePricePolicyRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    policy = await pricing_svc.create_price_policy(
        db, actor=make_actor(request, user), **body.model_dump()
    )
    await db.commit()
    return DataResponse(data=_policy_response(policy))


@router.post(
    "/platform/price-policies/{policy_id}/deactivate",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def deactivate_price_policy(
    policy_id: str,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    policy = await db.get(PricePolicy, policy_id)
    if policy is None:
        raise AppError("RATING_NOT_FOUND", "Price policy not found", 404)
    policy = await pricing_svc.deactivate_price_policy(
        db, policy, effective_until=datetime.now(UTC), actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=_policy_response(policy))


# ── FX ───────────────────────────────────────────────────────


@router.get("/platform/fx-rates", dependencies=[Depends(rate_limit(30, 60))])
async def list_fx_rates(
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        (await db.execute(select(FxRate).order_by(FxRate.effective_from.desc()).limit(200)))
        .scalars()
        .all()
    )
    data = [
        {
            "id": f.id,
            "base_currency": f.base_currency,
            "quote_currency": f.quote_currency,
            "rate": str(f.rate),
            "effective_from": f.effective_from.isoformat(),
            "effective_until": f.effective_until.isoformat() if f.effective_until else None,
        }
        for f in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post("/platform/fx-rates", status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def create_fx_rate(
    body: CreateFxRateRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    fx = await pricing_svc.create_fx_rate(
        db,
        actor=make_actor(request, user),
        base_currency=body.base_currency,
        quote_currency=body.quote_currency,
        rate=Decimal(body.rate),
        effective_from=body.effective_from,
        effective_until=body.effective_until,
    )
    await db.commit()
    return DataResponse(
        data={"id": fx.id, "pair": f"{fx.base_currency}/{fx.quote_currency}", "rate": str(fx.rate)}
    )


# ── Rated usage ──────────────────────────────────────────────


@router.get("/platform/rated-usage", dependencies=[Depends(rate_limit(30, 60))])
async def platform_rated_usage(
    tenant_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    usage_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    q = select(RatedUsage)
    if tenant_id:
        q = q.where(RatedUsage.tenant_id == tenant_id)
    if status:
        q = q.where(RatedUsage.status == status)
    if usage_type:
        q = q.where(RatedUsage.usage_type == usage_type)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(RatedUsage.rated_at.desc(), RatedUsage.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_platform_rated_response(r) for r in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.get("/tenants/{tenant_id}/rated-usage", dependencies=[Depends(rate_limit(30, 60))])
async def tenant_rated_usage(
    tenant_id: str,
    usage_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Billable side ONLY — internal cost, margin and FX never leave the
    platform scope (issue §11 acceptance)."""
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    q = select(RatedUsage).where(RatedUsage.tenant_id == tenant_id)
    if usage_type:
        q = q.where(RatedUsage.usage_type == usage_type)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(RatedUsage.rated_at.desc(), RatedUsage.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_tenant_rated_response(r) for r in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.post("/platform/rated-usage/{rated_id}/void", dependencies=[Depends(rate_limit(20, 60))])
async def void_rated_usage(
    rated_id: str,
    body: VoidRatedRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    row = await rating_svc.void_rated(
        db, rated_id, reason=body.reason, actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=_platform_rated_response(row))


@router.post("/platform/rating/run", dependencies=[Depends(rate_limit(10, 60))])
async def trigger_rating(
    tenant_id: str | None = Query(default=None),
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    count = await rating_svc.rate_pending(db, tenant_id=tenant_id)
    await db.commit()
    return DataResponse(data={"rated": count})


# ── Reconciliation ───────────────────────────────────────────


@router.post(
    "/platform/reconciliation/reports",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_recon_report(
    body: CreateReconReportRequest,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    year, month = int(body.period[:4]), int(body.period[5:7])
    # R76[2]: '0000' passes the regex but datetime rejects year 0 → 500.
    if year < 1:
        raise AppError("VALIDATION_ERROR", "period year out of range", 422)
    start = datetime(year, month, 1, tzinfo=UTC)
    end = datetime(year + (month == 12), (month % 12) + 1, 1, tzinfo=UTC)
    # R61[4]: platform_cost summed internal_cost_minor across rows whose
    # internal_cost_currency may differ (nothing pins a provider to one
    # currency — a superseding EUR cost rate mid-month splits the rows), and
    # the delta compared that mixed sum against a single-currency provider
    # figure. Quantity aggregates over ALL rows; cost aggregates ONLY rows in
    # the report's currency, and rows in other currencies are surfaced as a
    # count so the delta is never silently polluted.
    q = (
        select(
            func.coalesce(func.sum(UsageEvent.quantity), 0),
            func.coalesce(
                func.sum(RatedUsage.internal_cost_minor).filter(
                    RatedUsage.internal_cost_currency == body.currency
                ),
                0,
            ),
            func.count(RatedUsage.id).filter(RatedUsage.internal_cost_currency != body.currency),
        )
        .select_from(UsageEvent)
        .outerjoin(RatedUsage, RatedUsage.usage_event_id == UsageEvent.id)
        .where(
            UsageEvent.provider == body.provider,
            UsageEvent.usage_type == body.usage_type,
            UsageEvent.occurred_at >= start,
            UsageEvent.occurred_at < end,
        )
    )
    if body.model_or_service:
        q = q.where(UsageEvent.model_or_service == body.model_or_service)
    platform_qty, platform_cost, other_currency_rows = (await db.execute(q)).one()
    platform_cost = int(platform_cost)  # SUM+FILTER yields Decimal; the column is BigInteger
    report = ReconciliationReport(
        provider=body.provider,
        model_or_service=body.model_or_service,
        usage_type=body.usage_type,
        period=body.period,
        provider_reported_quantity=Decimal(body.provider_reported_quantity),
        provider_reported_cost_minor=body.provider_reported_cost_minor,
        currency=body.currency,
        platform_quantity=platform_qty,
        platform_cost_minor=platform_cost,
        delta_quantity=Decimal(body.provider_reported_quantity) - Decimal(platform_qty),
        delta_cost_minor=body.provider_reported_cost_minor - platform_cost,
        note=(
            f"[{other_currency_rows} rated rows in other currencies excluded from cost] "
            f"{body.note or ''}"
        ).strip()[:500]
        if other_currency_rows
        else body.note,
        created_by=user.id,
    )
    db.add(report)
    await db.commit()
    return DataResponse(
        data={
            "id": report.id,
            "period": report.period,
            "platform_quantity": str(report.platform_quantity),
            "platform_cost_minor": report.platform_cost_minor,
            "delta_quantity": str(report.delta_quantity),
            "delta_cost_minor": report.delta_cost_minor,
            "other_currency_rows": other_currency_rows,
            "status": report.status,
        }
    )


@router.get("/platform/reconciliation/reports", dependencies=[Depends(rate_limit(30, 60))])
async def list_recon_reports(
    status: str | None = Query(default=None),
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    q = select(ReconciliationReport)
    if status:
        q = q.where(ReconciliationReport.status == status)
    rows = (
        (await db.execute(q.order_by(ReconciliationReport.created_at.desc()).limit(100)))
        .scalars()
        .all()
    )
    data = [
        {
            "id": r.id,
            "provider": r.provider,
            "usage_type": r.usage_type,
            "period": r.period,
            "delta_quantity": str(r.delta_quantity),
            "delta_cost_minor": r.delta_cost_minor,
            "status": r.status,
        }
        for r in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.patch(
    "/platform/reconciliation/reports/{report_id}",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def resolve_recon_report(
    report_id: str,
    body: VoidRatedRequest,  # {reason} shape reused as resolved_note
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    report = await db.get(ReconciliationReport, report_id)
    if report is None:
        raise AppError("RATING_NOT_FOUND", "Report not found", 404)
    report.status = "resolved"
    report.resolved_note = body.reason
    report.resolved_at = datetime.now(UTC)
    await db.commit()
    return DataResponse(data={"id": report.id, "status": report.status})

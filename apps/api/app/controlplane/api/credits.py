"""Credit + budget endpoints (ADR-014 §5.5)."""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.credit import (
    BudgetPolicy,
    CreditLedgerEntry,
    CreditReservation,
    TenantCreditBalance,
)
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.services import credits as credit_svc
from app.controlplane.services import tenants as tenant_svc
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta, reject_ctrl_str

log = structlog.get_logger()

router = APIRouter(tags=["Credits & Budgets"])


# Money ceiling in minor units — well under int8 (9.2e18) so a valid amount
# can never overflow the BIGINT column (R88 class: unbounded amount → 500).
MAX_MINOR = 1_000_000_000_000_000  # 10^15


class AdjustCreditRequest(BaseModel):
    amount_minor: int = Field(ge=-MAX_MINOR, le=MAX_MINOR)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    reason: str = Field(min_length=3, max_length=500)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=120)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class GrantPromoRequest(BaseModel):
    amount_minor: int = Field(gt=0, le=MAX_MINOR)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    expires_at: datetime
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class BudgetPolicyRequest(BaseModel):
    scope_type: str = Field(pattern=r"^(tenant|org|project|cohort|user)$")
    scope_id: str | None = Field(default=None, min_length=26, max_length=26)
    period: str = Field(pattern=r"^(daily|monthly)$")
    capability_key: str | None = Field(default=None, max_length=64)
    usage_type: str | None = Field(default=None, max_length=40)
    limit_minor: int = Field(ge=0, le=MAX_MINOR)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    warning_threshold_pct: int = Field(default=80, ge=1, le=100)
    hard_stop: bool = True


class UpdateBudgetPolicyRequest(BaseModel):
    limit_minor: int | None = Field(default=None, ge=0, le=MAX_MINOR)
    warning_threshold_pct: int | None = Field(default=None, ge=1, le=100)
    hard_stop: bool | None = None
    is_active: bool | None = None


def _ledger_response(e: CreditLedgerEntry) -> dict:
    return {
        "id": e.id,
        "currency": e.currency,
        "entry_type": e.entry_type,
        "amount_minor": e.amount_minor,
        "balance_after_minor": e.balance_after_minor,
        "reference_type": e.reference_type,
        "reference_id": e.reference_id,
        "reason": e.reason,
        "expires_at": e.expires_at.isoformat() if e.expires_at else None,
        "created_at": e.created_at.isoformat(),
    }


def _budget_response(p: BudgetPolicy) -> dict:
    return {
        "id": p.id,
        "scope_type": p.scope_type,
        "scope_id": p.scope_id,
        "period": p.period,
        "capability_key": p.capability_key,
        "usage_type": p.usage_type,
        "limit_minor": p.limit_minor,
        "currency": p.currency,
        "warning_threshold_pct": p.warning_threshold_pct,
        "hard_stop": p.hard_stop,
        "is_active": p.is_active,
    }


# ── Tenant credit views ──────────────────────────────────────


@router.get("/tenants/{tenant_id}/credits", dependencies=[Depends(rate_limit(60, 60))])
async def credit_balances(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    rows = (
        (
            await db.execute(
                select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant_id)
            )
        )
        .scalars()
        .all()
    )
    data = [
        {
            "currency": b.currency,
            "balance_minor": b.balance_minor,
            "reserved_minor": b.reserved_minor,
            "available_minor": b.balance_minor - b.reserved_minor,
        }
        for b in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.get("/tenants/{tenant_id}/credits/ledger", dependencies=[Depends(rate_limit(30, 60))])
async def credit_ledger(
    tenant_id: str,
    currency: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    q = select(CreditLedgerEntry).where(CreditLedgerEntry.tenant_id == tenant_id)
    if currency:
        q = q.where(CreditLedgerEntry.currency == currency)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(CreditLedgerEntry.created_at.desc()).offset(offset).limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_ledger_response(e) for e in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.get("/tenants/{tenant_id}/reservations", dependencies=[Depends(rate_limit(30, 60))])
async def list_reservations(
    tenant_id: str,
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    q = select(CreditReservation).where(CreditReservation.tenant_id == tenant_id)
    if status:
        q = q.where(CreditReservation.status == status)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(CreditReservation.created_at.desc()).offset(offset).limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    data = [
        {
            "id": r.id,
            "currency": r.currency,
            "amount_minor": r.amount_minor,
            "status": r.status,
            "reference_type": r.reference_type,
            "reference_id": r.reference_id,
            "settled_amount_minor": r.settled_amount_minor,
            "expires_at": r.expires_at.isoformat(),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


# ── Platform credit ops ──────────────────────────────────────


@router.post(
    "/platform/tenants/{tenant_id}/credits/adjust",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def platform_adjust_credit(
    tenant_id: str,
    body: AdjustCreditRequest,
    request: Request,
    user: User = Depends(require_platform_role("billing_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    entry = await credit_svc.adjust(
        db,
        tenant_id,
        body.currency,
        body.amount_minor,
        reason=body.reason,
        actor=make_actor(request, user),
        idempotency_key=body.idempotency_key,
    )
    await db.commit()
    if entry is None:
        return DataResponse(data={"duplicate": True})
    return DataResponse(data=_ledger_response(entry))


@router.post(
    "/platform/tenants/{tenant_id}/credits/grant-promotional",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def grant_promotional(
    tenant_id: str,
    body: GrantPromoRequest,
    request: Request,
    user: User = Depends(require_platform_role("billing_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    entry = await credit_svc.grant_promotional(
        db,
        tenant_id,
        body.currency,
        body.amount_minor,
        expires_at=body.expires_at,
        reason=body.reason,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(data=_ledger_response(entry))


# ── Budgets ──────────────────────────────────────────────────


@router.get("/tenants/{tenant_id}/budgets", dependencies=[Depends(rate_limit(30, 60))])
async def list_budgets(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    rows = (
        (
            await db.execute(
                select(BudgetPolicy)
                .where(BudgetPolicy.tenant_id == tenant_id)
                .order_by(BudgetPolicy.created_at)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_budget_response(p) for p in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


@router.post(
    "/tenants/{tenant_id}/budgets",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_budget(
    tenant_id: str,
    body: BudgetPolicyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner", "billing_admin")
    if body.scope_type != "tenant" and body.scope_id is None:
        raise AppError("VALIDATION_ERROR", "scope_id required for non-tenant scope", 422)
    if body.scope_type == "tenant" and body.scope_id is not None:
        raise AppError("VALIDATION_ERROR", "tenant scope takes no scope_id", 422)
    dup = (
        await db.execute(
            select(BudgetPolicy.id).where(
                BudgetPolicy.tenant_id == tenant_id,
                BudgetPolicy.scope_type == body.scope_type,
                (
                    BudgetPolicy.scope_id == body.scope_id
                    if body.scope_id
                    else BudgetPolicy.scope_id.is_(None)
                ),
                BudgetPolicy.period == body.period,
                (
                    BudgetPolicy.capability_key == body.capability_key
                    if body.capability_key
                    else BudgetPolicy.capability_key.is_(None)
                ),
                (
                    BudgetPolicy.usage_type == body.usage_type
                    if body.usage_type
                    else BudgetPolicy.usage_type.is_(None)
                ),
            )
        )
    ).scalar_one_or_none()
    if dup is not None:
        raise AppError("BUDGET_POLICY_CONFLICT", "A policy with these dimensions exists", 409)
    policy = BudgetPolicy(tenant_id=tenant_id, created_by=user.id, **body.model_dump())
    db.add(policy)
    await db.commit()
    return DataResponse(data=_budget_response(policy))


@router.patch(
    "/tenants/{tenant_id}/budgets/{policy_id}", dependencies=[Depends(rate_limit(20, 60))]
)
async def update_budget(
    tenant_id: str,
    policy_id: str,
    body: UpdateBudgetPolicyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner", "billing_admin")
    policy = await db.get(BudgetPolicy, policy_id)
    if policy is None or policy.tenant_id != tenant_id:
        raise AppError("BUDGET_POLICY_NOT_FOUND", "Budget policy not found", 404)
    for field_name, value in body.model_dump(exclude_unset=True).items():
        setattr(policy, field_name, value)
    await db.commit()
    return DataResponse(data=_budget_response(policy))


@router.delete(
    "/tenants/{tenant_id}/budgets/{policy_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def delete_budget(
    tenant_id: str,
    policy_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner", "billing_admin")
    policy = await db.get(BudgetPolicy, policy_id)
    if policy is None or policy.tenant_id != tenant_id:
        raise AppError("BUDGET_POLICY_NOT_FOUND", "Budget policy not found", 404)
    await db.delete(policy)
    await db.commit()

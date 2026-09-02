"""Partner endpoints: CRUD, attribution, rules, entries, statements + CSV
(ADR-014 §7.4). Cross-partner isolation = uniform 404 everywhere."""

import csv
import io
from datetime import datetime
from decimal import Decimal

import structlog
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.partner import (
    PARTNER_TYPES,
    RULE_TYPES,
    Partner,
    PartnerMember,
    RevenueShareEntry,
    RevenueShareRule,
    SettlementStatement,
)
from app.controlplane.models.plan import PlanVersion, ProductPlan
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.services import revenue_share as revshare_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import record_audit
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import (
    DataResponse,
    ListResponse,
    PaginationMeta,
    reject_ctrl_str,
    safe_decimal,
)

log = structlog.get_logger()

router = APIRouter(tags=["Partners"])

_BILLING_ROLES = ("billing_admin", "platform_admin")


async def require_partner_member(
    db: AsyncSession, partner_id: str, user: User, *roles: str
) -> PartnerMember:
    """Uniform 404 — membership must not be an existence oracle."""
    partner = await db.get(Partner, partner_id)
    if partner is None:
        raise AppError("PARTNER_NOT_FOUND", "Partner not found", 404)
    if await tenant_svc.has_platform_role(db, user, "platform_admin", "billing_admin"):
        return PartnerMember(partner_id=partner_id, user_id=user.id, role="admin")
    member = (
        await db.execute(
            select(PartnerMember).where(
                PartnerMember.partner_id == partner_id, PartnerMember.user_id == user.id
            )
        )
    ).scalar_one_or_none()
    if member is None:
        raise AppError("PARTNER_NOT_FOUND", "Partner not found", 404)
    if roles and member.role not in roles:
        raise AppError("PARTNER_FORBIDDEN", "Insufficient partner permissions", 403)
    return member


class CreatePartnerRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    partner_type: str
    contact_email: EmailStr | None = None
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")

    @field_validator("name")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class PartnerMemberRequest(BaseModel):
    user_id: str = Field(min_length=26, max_length=26)
    role: str = Field(pattern=r"^(admin|member)$")


class AttributionRequest(BaseModel):
    partner_id: str = Field(min_length=26, max_length=26)


class CreateRuleRequest(BaseModel):
    beneficiary_type: str = Field(pattern=r"^(partner|seller_org)$")
    partner_id: str | None = Field(default=None, min_length=26, max_length=26)
    revenue_type: str = Field(pattern=r"^(subscription|usage|marketplace|all)$")
    tenant_id: str | None = Field(default=None, min_length=26, max_length=26)
    plan_id: str | None = Field(default=None, min_length=26, max_length=26)
    listing_id: str | None = Field(default=None, min_length=26, max_length=26)
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    rule_type: str
    rate: str | None = None
    amount_minor: int | None = Field(default=None, ge=0, le=1_000_000_000_000_000)
    amount_currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    effective_from: datetime

    @field_validator("rate")
    @classmethod
    def _rate(cls, v, info):
        if v is None:
            return v
        # Column is Numeric(9,6): integer part < 10^3. A NaN/Infinity or an
        # over-range value would otherwise overflow the INSERT → 500.
        d = safe_decimal(v, info.field_name)
        if not d.is_finite() or d < 0 or d >= Decimal("1000"):
            raise ValueError("rate must be non-negative and < 1000")
        return v


class StatementGenerateRequest(BaseModel):
    beneficiary_type: str = Field(pattern=r"^(partner|seller_org)$")
    partner_id: str | None = Field(default=None, min_length=26, max_length=26)
    beneficiary_org_id: str | None = Field(default=None, min_length=26, max_length=26)
    period: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


class StatementAdjustRequest(BaseModel):
    amount_minor: int = Field(ge=-1_000_000_000_000_000, le=1_000_000_000_000_000)
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class MarkPaidRequest(BaseModel):
    external_payment_ref: str = Field(min_length=1, max_length=120)

    @field_validator("external_payment_ref")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


def _partner_response(p: Partner) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "partner_type": p.partner_type,
        "status": p.status,
        "contact_email": p.contact_email,
        "country": p.country,
        "currency": p.currency,
        "created_at": p.created_at.isoformat(),
    }


def _margin_based(e: RevenueShareEntry) -> bool:
    """R60[39]: for percentage_of_margin rules revenue_base_minor IS the
    platform's internal margin (billable − cost) — never partner-visible."""
    return (e.rule_snapshot or {}).get("rule_type") == "percentage_of_margin"


def _entry_response(e: RevenueShareEntry) -> dict:
    return {
        "id": e.id,
        "beneficiary_type": e.beneficiary_type,
        "source_type": e.source_type,
        "source_id": e.source_id,
        "rule_snapshot": e.rule_snapshot,
        "revenue_base_minor": None if _margin_based(e) else e.revenue_base_minor,
        "share_amount_minor": e.share_amount_minor,
        "currency": e.currency,
        "period": e.period,
        "status": e.status,
        "adjustment_of_id": e.adjustment_of_id,
        "created_at": e.created_at.isoformat(),
    }


def _statement_response(s: SettlementStatement) -> dict:
    return {
        "id": s.id,
        "beneficiary_type": s.beneficiary_type,
        "partner_id": s.partner_id,
        "beneficiary_org_id": s.beneficiary_org_id,
        "period": s.period,
        "status": s.status,
        "currency": s.currency,
        "opening_adjustments_minor": s.opening_adjustments_minor,
        "gross_revenue_minor": s.gross_revenue_minor,
        "refunds_minor": s.refunds_minor,
        "share_total_minor": s.share_total_minor,
        "manual_adjustments_minor": s.manual_adjustments_minor,
        "net_amount_minor": s.net_amount_minor,
        "finalized_at": s.finalized_at.isoformat() if s.finalized_at else None,
        "external_payment_ref": s.external_payment_ref,
    }


# ── Platform partner CRUD + attribution ──────────────────────


@router.post("/platform/partners", status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_partner(
    body: CreatePartnerRequest,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    if body.partner_type not in PARTNER_TYPES:
        raise AppError("VALIDATION_ERROR", f"Unknown partner type '{body.partner_type}'", 422)
    dup = (
        await db.execute(select(Partner.id).where(Partner.slug == body.slug).limit(1))
    ).scalar_one_or_none()
    if dup is not None:
        raise AppError("VALIDATION_ERROR", "Partner slug already in use", 409)
    partner = Partner(created_by=user.id, **body.model_dump())
    db.add(partner)
    await db.commit()
    return DataResponse(data=_partner_response(partner))


@router.get("/platform/partners", dependencies=[Depends(rate_limit(30, 60))])
async def list_partners(
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(require_platform_role(*_BILLING_ROLES, "platform_support")),
    db: AsyncSession = Depends(get_db),
):
    # R76[3]: fixed limit(200) + fabricated meta hid partners past the cap.
    total = (await db.execute(select(func.count(Partner.id)))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                select(Partner)
                .order_by(Partner.created_at.desc(), Partner.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_partner_response(p) for p in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.post(
    "/platform/partners/{partner_id}/members",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def add_partner_member(
    partner_id: str,
    body: PartnerMemberRequest,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    partner = await db.get(Partner, partner_id)
    if partner is None:
        raise AppError("PARTNER_NOT_FOUND", "Partner not found", 404)
    target = await db.get(User, body.user_id)
    if target is None:
        raise AppError("USER_NOT_FOUND", "User not found", 404)
    dup = (
        await db.execute(
            select(PartnerMember.id).where(
                PartnerMember.partner_id == partner_id,
                PartnerMember.user_id == body.user_id,
            )
        )
    ).scalar_one_or_none()
    if dup is not None:
        raise AppError("VALIDATION_ERROR", "Already a partner member", 409)
    member = PartnerMember(
        partner_id=partner_id, user_id=body.user_id, role=body.role, created_by=user.id
    )
    db.add(member)
    await db.commit()
    return DataResponse(data={"id": member.id, "role": member.role})


@router.put(
    "/platform/tenants/{tenant_id}/partner-attribution",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def set_attribution(
    tenant_id: str,
    body: AttributionRequest,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    from datetime import UTC

    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    partner = await db.get(Partner, body.partner_id)
    if partner is None:
        raise AppError("PARTNER_NOT_FOUND", "Partner not found", 404)
    before = {"partner_id": tenant.partner_id}
    tenant.partner_id = partner.id
    tenant.attributed_at = datetime.now(UTC)
    await record_audit(
        db,
        actor=make_actor(request, user),
        action="tenant.attribution_set",
        target_type="tenant",
        target_id=tenant.id,
        tenant_id=tenant.id,
        partner_id=partner.id,
        before=before,
        after={"partner_id": partner.id},
    )
    await db.commit()
    return DataResponse(data={"tenant_id": tenant.id, "partner_id": partner.id})


@router.delete(
    "/platform/tenants/{tenant_id}/partner-attribution",
    status_code=204,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def clear_attribution(
    tenant_id: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    before = {"partner_id": tenant.partner_id}
    tenant.partner_id = None
    tenant.attributed_at = None
    await record_audit(
        db,
        actor=make_actor(request, user),
        action="tenant.attribution_cleared",
        target_type="tenant",
        target_id=tenant.id,
        tenant_id=tenant.id,
        before=before,
    )
    await db.commit()


# ── Revenue-share rules ──────────────────────────────────────


@router.post(
    "/platform/revenue-share-rules",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_rule(
    body: CreateRuleRequest,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    if body.rule_type not in RULE_TYPES:
        raise AppError("RULE_PARAM_INVALID", f"Unknown rule type '{body.rule_type}'", 422)
    is_pct = body.rule_type.startswith("percentage")
    if is_pct:
        if body.rate is None or body.amount_minor is not None:
            raise AppError("RULE_PARAM_INVALID", "Percentage rules take rate only", 422)
        rate = Decimal(body.rate)
        if not rate.is_finite() or rate < 0 or rate > 100:
            raise AppError("RULE_PARAM_INVALID", "rate must be 0-100", 422)
    else:
        if body.amount_minor is None or body.rate is not None:
            raise AppError("RULE_PARAM_INVALID", "Fixed rules take amount_minor only", 422)
        rate = None
    if body.beneficiary_type == "partner" and body.partner_id is None:
        raise AppError("RULE_PARAM_INVALID", "partner rules need partner_id", 422)
    # Next version for this dimension set
    dims = [
        RevenueShareRule.beneficiary_type == body.beneficiary_type,
        (
            RevenueShareRule.partner_id == body.partner_id
            if body.partner_id
            else RevenueShareRule.partner_id.is_(None)
        ),
        RevenueShareRule.revenue_type == body.revenue_type,
        (
            RevenueShareRule.tenant_id == body.tenant_id
            if body.tenant_id
            else RevenueShareRule.tenant_id.is_(None)
        ),
        (
            RevenueShareRule.plan_id == body.plan_id
            if body.plan_id
            else RevenueShareRule.plan_id.is_(None)
        ),
        (
            RevenueShareRule.listing_id == body.listing_id
            if body.listing_id
            else RevenueShareRule.listing_id.is_(None)
        ),
    ]
    latest = (
        await db.execute(select(func.max(RevenueShareRule.version)).where(*dims))
    ).scalar_one()
    rule = RevenueShareRule(
        version=(latest or 0) + 1,
        rate=rate,
        created_by=user.id,
        **body.model_dump(exclude={"rate"}),
    )
    db.add(rule)
    await db.commit()
    return DataResponse(data={"id": rule.id, "version": rule.version, "status": rule.status})


@router.post(
    "/platform/revenue-share-rules/{rule_id}/activate",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def activate_rule(
    rule_id: str,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    rule = await db.get(RevenueShareRule, rule_id)
    if rule is None:
        raise AppError("PARTNER_NOT_FOUND", "Rule not found", 404)
    rule = await revshare_svc.activate_rule(db, rule, actor=make_actor(request, user))
    await db.commit()
    return DataResponse(data={"id": rule.id, "status": rule.status, "version": rule.version})


@router.get("/platform/revenue-share-rules", dependencies=[Depends(rate_limit(30, 60))])
async def list_rules(
    partner_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    q = select(RevenueShareRule)
    if partner_id:
        q = q.where(RevenueShareRule.partner_id == partner_id)
    # R76[3]: fixed limit(200) + fabricated meta hid rules past the cap.
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(RevenueShareRule.created_at.desc(), RevenueShareRule.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    data = [
        {
            "id": r.id,
            "beneficiary_type": r.beneficiary_type,
            "partner_id": r.partner_id,
            "revenue_type": r.revenue_type,
            "rule_type": r.rule_type,
            "rate": str(r.rate) if r.rate is not None else None,
            "amount_minor": r.amount_minor,
            "version": r.version,
            "status": r.status,
            "effective_from": r.effective_from.isoformat(),
        }
        for r in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


# ── Partner-facing views ─────────────────────────────────────


@router.get("/partners/mine", dependencies=[Depends(rate_limit(60, 60))])
async def my_partners(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(Partner, PartnerMember.role)
            .join(PartnerMember, PartnerMember.partner_id == Partner.id)
            .where(PartnerMember.user_id == user.id)
        )
    ).all()
    data = [{**_partner_response(p), "my_role": role} for p, role in rows]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.get("/partners/{partner_id}", dependencies=[Depends(rate_limit(60, 60))])
async def get_partner(
    partner_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_partner_member(db, partner_id, user)
    partner = await db.get(Partner, partner_id)
    return DataResponse(data=_partner_response(partner))


@router.get("/partners/{partner_id}/tenants", dependencies=[Depends(rate_limit(30, 60))])
async def partner_tenants(
    partner_id: str,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Attributed tenants — COMMERCIAL METADATA ONLY (name/status/plan/created);
    no usage or revenue detail (issue §22)."""
    await require_partner_member(db, partner_id, user, "admin")
    # R76[4]: was unbounded (no LIMIT) with 3 queries per row (live sub,
    # version, plan) — a big-book partner degraded into hundreds of point
    # lookups per request. Paginate + resolve the plan key in ONE joined
    # query for the page.
    from app.controlplane.models.billing import Subscription

    base = select(TenantAccount).where(TenantAccount.partner_id == partner_id)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        await db.execute(
            select(TenantAccount, ProductPlan.key)
            .outerjoin(
                Subscription,
                (Subscription.tenant_id == TenantAccount.id) & (Subscription.status != "cancelled"),
            )
            .outerjoin(PlanVersion, PlanVersion.id == Subscription.plan_version_id)
            .outerjoin(ProductPlan, ProductPlan.id == PlanVersion.plan_id)
            .where(TenantAccount.partner_id == partner_id)
            .order_by(TenantAccount.created_at.desc(), TenantAccount.id.desc())
            .offset(offset)
            .limit(per_page)
        )
    ).all()
    data = [
        {
            "tenant_id": t.id,
            "name": t.name,
            "slug": t.slug,
            "status": t.status.value,
            "plan_key": plan_key,
            "created_at": t.created_at.isoformat(),
        }
        for t, plan_key in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.get(
    "/partners/{partner_id}/revenue-share-entries",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def partner_entries(
    partner_id: str,
    period: str | None = Query(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_partner_member(db, partner_id, user)
    q = select(RevenueShareEntry).where(RevenueShareEntry.partner_id == partner_id)
    if period:
        q = q.where(RevenueShareEntry.period == period)
    if status:
        q = q.where(RevenueShareEntry.status == status)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(RevenueShareEntry.created_at.desc(), RevenueShareEntry.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_entry_response(e) for e in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.get("/partners/{partner_id}/statements", dependencies=[Depends(rate_limit(30, 60))])
async def partner_statements(
    partner_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_partner_member(db, partner_id, user)
    rows = (
        (
            await db.execute(
                select(SettlementStatement)
                .where(SettlementStatement.partner_id == partner_id)
                .order_by(SettlementStatement.period.desc())
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_statement_response(s) for s in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


@router.get(
    "/partners/{partner_id}/statements/{statement_id}",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def partner_statement_detail(
    partner_id: str,
    statement_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_partner_member(db, partner_id, user)
    statement = await db.get(SettlementStatement, statement_id)
    if statement is None or statement.partner_id != partner_id:
        raise AppError("PARTNER_NOT_FOUND", "Statement not found", 404)
    entries = (
        (
            await db.execute(
                select(RevenueShareEntry).where(RevenueShareEntry.statement_id == statement.id)
            )
        )
        .scalars()
        .all()
    )
    data = _statement_response(statement)
    data["entries"] = [_entry_response(e) for e in entries]
    data["entry_count"] = len(entries)
    return DataResponse(data=data)


@router.get(
    "/partners/{partner_id}/statements/{statement_id}/export.csv",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def export_statement_csv(
    partner_id: str,
    statement_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_partner_member(db, partner_id, user)
    statement = await db.get(SettlementStatement, statement_id)
    if statement is None or statement.partner_id != partner_id:
        raise AppError("PARTNER_NOT_FOUND", "Statement not found", 404)
    entries = (
        (
            await db.execute(
                select(RevenueShareEntry)
                .where(RevenueShareEntry.statement_id == statement.id)
                .order_by(RevenueShareEntry.created_at)
            )
        )
        .scalars()
        .all()
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "entry_id",
            "period",
            "source_type",
            "source_id",
            "rule_type",
            "rule_version",
            "revenue_base_minor",
            "share_amount_minor",
            "currency",
            "status",
            "created_at",
        ]
    )
    for e in entries:
        writer.writerow(
            [
                e.id,
                e.period,
                e.source_type,
                e.source_id,
                (e.rule_snapshot or {}).get("rule_type", ""),
                (e.rule_snapshot or {}).get("version", ""),
                # R60[39]: margin-based entries' base IS the platform margin.
                "" if _margin_based(e) else e.revenue_base_minor,
                e.share_amount_minor,
                e.currency,
                e.status,
                e.created_at.isoformat(),
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="statement-{statement.period}-{statement.id}.csv"'
            )
        },
    )


# ── Platform settlement ops ──────────────────────────────────


@router.post(
    "/platform/settlements/generate",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def generate_statement(
    body: StatementGenerateRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    statement = await revshare_svc.generate_statement(
        db,
        beneficiary_type=body.beneficiary_type,
        partner_id=body.partner_id,
        beneficiary_org_id=body.beneficiary_org_id,
        period=body.period,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(data=_statement_response(statement))


async def _do_statement_transition(
    db: AsyncSession,
    statement_id: str,
    action: str,
    request: Request,
    user: User,
    external_payment_ref: str | None = None,
) -> DataResponse:
    statement = await db.get(SettlementStatement, statement_id)
    if statement is None:
        raise AppError("PARTNER_NOT_FOUND", "Statement not found", 404)
    statement = await revshare_svc.transition_statement(
        db,
        statement,
        action,
        actor=make_actor(request, user),
        external_payment_ref=external_payment_ref,
    )
    await db.commit()
    return DataResponse(data=_statement_response(statement))


@router.post(
    "/platform/settlements/{statement_id}/finalize",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def finalize_statement(
    statement_id: str,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    return await _do_statement_transition(db, statement_id, "finalize", request, user)


@router.post(
    "/platform/settlements/{statement_id}/approve",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def approve_statement(
    statement_id: str,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    return await _do_statement_transition(db, statement_id, "approve", request, user)


@router.post(
    "/platform/settlements/{statement_id}/mark-paid",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def mark_statement_paid(
    statement_id: str,
    body: MarkPaidRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    return await _do_statement_transition(
        db, statement_id, "mark-paid", request, user, body.external_payment_ref
    )


@router.post(
    "/platform/settlements/{statement_id}/adjust",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def adjust_statement(
    statement_id: str,
    body: StatementAdjustRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    statement = await db.get(SettlementStatement, statement_id)
    if statement is None:
        raise AppError("PARTNER_NOT_FOUND", "Statement not found", 404)
    statement = await revshare_svc.adjust_statement(
        db,
        statement,
        amount_minor=body.amount_minor,
        reason=body.reason,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(data=_statement_response(statement))

"""Marketplace endpoints: listings, purchases, licenses, earnings
(ADR-014 §8.7)."""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.marketplace import (
    LicenseGrant,
    MarketplaceListing,
    MarketplacePurchase,
)
from app.controlplane.models.partner import RevenueShareEntry
from app.controlplane.services import marketplace as market_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import record_audit
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta, reject_ctrl_str

log = structlog.get_logger()

router = APIRouter(tags=["Marketplace"])

_BILLING_ROLES = ("billing_admin", "platform_admin")
_ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


class CreateListingRequest(BaseModel):
    product_type: str = Field(pattern=r"^(skill_pack|workflow_pack|learning_path)$")
    product_id: str = Field(min_length=26, max_length=26)
    offer_type: str = Field(pattern=r"^(free|paid|private|partner_only|included_with_plan)$")
    price_minor: int | None = Field(default=None, gt=0, le=10_000_000_000)
    currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    license_scope: str = Field(
        default="organization", pattern=r"^(tenant|organization|cohort|seat_limited)$"
    )
    seat_limit: int | None = Field(default=None, gt=0, le=1_000_000)
    upgrade_policy: str = Field(default="all_versions", pattern=r"^(all_versions|major_locked)$")
    included_plan_keys: list[str] = Field(default_factory=list, max_length=10)
    bill_via_invoice: bool = False


class PurchaseRequest(BaseModel):
    listing_id: str = Field(min_length=26, max_length=26)
    payment_method: str = Field(pattern=r"^(credit|checkout)$")
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=120)


class ManualGrantRequest(BaseModel):
    product_type: str = Field(pattern=r"^(skill_pack|workflow_pack|learning_path)$")
    product_id: str = Field(min_length=26, max_length=26)
    tenant_id: str = Field(min_length=26, max_length=26)
    scope: str = Field(pattern=r"^(tenant|organization|cohort|seat_limited)$")
    org_id: str | None = Field(default=None, min_length=26, max_length=26)
    expires_at: datetime | None = None


class ReasonRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class CommissionRequest(BaseModel):
    platform_commission_pct: str  # decimal string 0-100


def _listing_response(listing: MarketplaceListing, *, public: bool = False) -> dict:
    data = {
        "id": listing.id,
        "product_type": listing.product_type,
        "product_id": listing.product_id,
        "offer_type": listing.offer_type,
        "price_minor": listing.price_minor,
        "currency": listing.currency,
        "license_scope": listing.license_scope,
        "seat_limit": listing.seat_limit,
        "upgrade_policy": listing.upgrade_policy,
        "included_plan_keys": listing.included_plan_keys,
        "status": listing.status,
    }
    if not public:
        data["seller_org_id"] = listing.seller_org_id
        data["platform_commission_pct"] = str(listing.platform_commission_pct)
        data["bill_via_invoice"] = listing.bill_via_invoice
    return data


def _purchase_response(p: MarketplacePurchase) -> dict:
    """Buyer-facing: economics internals (fee/seller/partner splits) whitelisted OUT."""
    return {
        "id": p.id,
        "listing_id": p.listing_id,
        "status": p.status,
        "amount_minor": p.amount_minor,
        "currency": p.currency,
        "payment_method": p.payment_method,
        "created_at": p.created_at.isoformat(),
    }


def _grant_response(g: LicenseGrant) -> dict:
    return {
        "id": g.id,
        "product_type": g.product_type,
        "product_id": g.product_id,
        "org_id": g.org_id,
        "scope": g.scope,
        "seat_limit": g.seat_limit,
        "status": g.status,
        "source": g.source,
        "starts_at": g.starts_at.isoformat(),
        "expires_at": g.expires_at.isoformat() if g.expires_at else None,
    }


# ── Seller listings ──────────────────────────────────────────


@router.get("/orgs/{org_id}/marketplace/listings", dependencies=[Depends(rate_limit(30, 60))])
async def seller_listings(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *_ADMIN_ROLES)
    rows = (
        (
            await db.execute(
                select(MarketplaceListing).where(MarketplaceListing.seller_org_id == org_id)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_listing_response(listing) for listing in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


@router.post(
    "/orgs/{org_id}/marketplace/listings",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_listing(
    org_id: str,
    body: CreateListingRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *_ADMIN_ROLES)
    from app.controlplane import facade

    tenant = await facade.get_tenant_for_org(db, org_id)
    facade.require_tenant_active(tenant)
    await facade.require_feature(db, tenant, "paid_marketplace")
    listing = await market_svc.create_listing(
        db,
        seller_org_id=org_id,
        actor=make_actor(request, user, "tenant"),
        **body.model_dump(),
    )
    await db.commit()
    return DataResponse(data=_listing_response(listing))


@router.post(
    "/orgs/{org_id}/marketplace/listings/{listing_id}/activate",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def activate_listing(
    org_id: str,
    listing_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *_ADMIN_ROLES)
    listing = await db.get(MarketplaceListing, listing_id)
    if listing is None or listing.seller_org_id != org_id:
        raise AppError("LISTING_INVALID", "Listing not found", 404)
    listing.status = "active"
    await db.commit()
    return DataResponse(data=_listing_response(listing))


@router.post(
    "/orgs/{org_id}/marketplace/listings/{listing_id}/delist",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delist_listing(
    org_id: str,
    listing_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *_ADMIN_ROLES)
    listing = await db.get(MarketplaceListing, listing_id)
    if listing is None or listing.seller_org_id != org_id:
        raise AppError("LISTING_INVALID", "Listing not found", 404)
    listing.status = "delisted"
    await db.commit()
    return DataResponse(data=_listing_response(listing))


# ── Public registry price badges ─────────────────────────────


@router.get("/registry/listings", dependencies=[Depends(rate_limit(60, 60))])
async def registry_listings(
    product_type: str = Query(pattern=r"^(skill_pack|workflow_pack|learning_path)$"),
    product_ids: str = Query(max_length=2000),
    db: AsyncSession = Depends(get_db),
):
    """Batch price badges for registry cards (≤50 ids, public)."""
    ids = [i.strip() for i in product_ids.split(",") if i.strip()][:50]
    rows = (
        (
            await db.execute(
                select(MarketplaceListing).where(
                    MarketplaceListing.product_type == product_type,
                    MarketplaceListing.product_id.in_(ids),
                    MarketplaceListing.status == "active",
                )
            )
        )
        .scalars()
        .all()
    )
    from app.models.organization import Organization

    data = {}
    for listing in rows:
        seller = await db.get(Organization, listing.seller_org_id)
        data[listing.product_id] = {
            **_listing_response(listing, public=True),
            "seller_org_name": seller.name if seller else None,
        }
    return DataResponse(data=data)


@router.get(
    "/orgs/{org_id}/marketplace/license-status",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def license_status(
    org_id: str,
    product_type: str = Query(pattern=r"^(skill_pack|workflow_pack|learning_path)$"),
    product_ids: str = Query(max_length=2000),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    from app.controlplane import facade

    tenant = await facade.get_tenant_for_org(db, org_id)
    ids = [i.strip() for i in product_ids.split(",") if i.strip()][:50]
    data = {}
    for product_id in ids:
        grant = await market_svc._find_covering_grant(
            db, product_type, product_id, tenant.id, org_id
        )
        data[product_id] = {"licensed": grant is not None}
    return DataResponse(data=data)


# ── Purchases ────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/marketplace/purchases",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def purchase(
    org_id: str,
    body: PurchaseRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *_ADMIN_ROLES)
    from app.controlplane import facade

    tenant = await facade.get_tenant_for_org(db, org_id)
    facade.require_tenant_active(tenant)
    actor = make_actor(request, user, "tenant")
    purchase_row = await market_svc.create_purchase(
        db,
        listing_id=body.listing_id,
        buyer_org_id=org_id,
        purchaser=actor,
        payment_method=body.payment_method,
        idempotency_key=body.idempotency_key,
    )
    if purchase_row.status == "paid":
        await db.commit()
        return DataResponse(data=_purchase_response(purchase_row))
    if body.payment_method == "credit":
        from app.controlplane.services import credits as credit_svc

        await credit_svc.debit(
            db,
            purchase_row.buyer_tenant_id,
            purchase_row.currency,
            purchase_row.amount_minor,
            reference_type="purchase",
            reference_id=purchase_row.id,
            idempotency_key=f"purchase:{purchase_row.id}",
            created_by=user.id,
        )
        purchase_row = await market_svc.mark_purchase_paid(
            db, purchase_id=purchase_row.id, payment_ref=None, actor=actor
        )
        await db.commit()
        return DataResponse(data=_purchase_response(purchase_row))
    # checkout: hosted session via the tenant's billing provider (mock/stripe)
    from app.config import settings
    from app.controlplane.services.billing_providers import get_billing_provider

    provider_key = "stripe" if settings.stripe_secret_key else settings.billing_provider_default
    if provider_key == "manual":
        provider_key = "mock"
    adapter = get_billing_provider(provider_key)
    session = await adapter.create_checkout_session(
        tenant=tenant,
        kind="purchase",
        amount_minor=purchase_row.amount_minor,
        currency=purchase_row.currency,
        success_url=f"{settings.frontend_url}/dashboard/orgs/{org_id}/packs?purchased=1",
        cancel_url=f"{settings.frontend_url}/dashboard/orgs/{org_id}/packs?cancelled=1",
        metadata={"purchase_id": purchase_row.id},
    )
    purchase_row.payment_ref = session.session_ref
    await db.commit()
    return DataResponse(data={**_purchase_response(purchase_row), "checkout_url": session.url})


@router.get("/tenants/{tenant_id}/licenses", dependencies=[Depends(rate_limit(30, 60))])
async def tenant_licenses(
    tenant_id: str,
    status: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    q = select(LicenseGrant).where(LicenseGrant.tenant_id == tenant_id)
    if status:
        q = q.where(LicenseGrant.status == status)
    rows = (await db.execute(q.order_by(LicenseGrant.created_at.desc()))).scalars().all()
    return ListResponse(
        data=[_grant_response(g) for g in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


@router.get("/tenants/{tenant_id}/purchases", dependencies=[Depends(rate_limit(30, 60))])
async def tenant_purchases(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    rows = (
        (
            await db.execute(
                select(MarketplacePurchase)
                .where(MarketplacePurchase.buyer_tenant_id == tenant_id)
                .order_by(MarketplacePurchase.created_at.desc())
                .limit(100)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_purchase_response(p) for p in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


# ── Seller earnings ──────────────────────────────────────────


@router.get("/orgs/{org_id}/marketplace/earnings", dependencies=[Depends(rate_limit(30, 60))])
async def seller_earnings(
    org_id: str,
    period: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *_ADMIN_ROLES)
    q = select(
        RevenueShareEntry.period,
        RevenueShareEntry.currency,
        func.sum(RevenueShareEntry.share_amount_minor).label("total"),
        func.count(RevenueShareEntry.id).label("entries"),
    ).where(RevenueShareEntry.beneficiary_org_id == org_id)
    if period:
        q = q.where(RevenueShareEntry.period == period)
    rows = (
        await db.execute(
            q.group_by(RevenueShareEntry.period, RevenueShareEntry.currency).order_by(
                RevenueShareEntry.period.desc()
            )
        )
    ).all()
    data = [
        {
            "period": r.period,
            "currency": r.currency,
            "total_minor": int(r.total),
            "entry_count": int(r.entries),
        }
        for r in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


# ── Platform ops ─────────────────────────────────────────────


@router.post("/platform/licenses", status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def manual_grant(
    body: ManualGrantRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    grant = await market_svc.manual_grant(db, actor=make_actor(request, user), **body.model_dump())
    await db.commit()
    return DataResponse(data=_grant_response(grant))


@router.post("/platform/licenses/{grant_id}/revoke", dependencies=[Depends(rate_limit(20, 60))])
async def revoke_license(
    grant_id: str,
    body: ReasonRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    grant = await market_svc.revoke_grant(
        db, grant_id, reason=body.reason, actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=_grant_response(grant))


@router.post(
    "/platform/purchases/{purchase_id}/mark-paid",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def platform_mark_paid(
    purchase_id: str,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    purchase_row = await market_svc.mark_purchase_paid(
        db, purchase_id=purchase_id, payment_ref="manual", actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=_purchase_response(purchase_row))


@router.post(
    "/platform/purchases/{purchase_id}/refund",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def refund_purchase(
    purchase_id: str,
    body: ReasonRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    purchase_row = await market_svc.refund_purchase(
        db, purchase_id, reason=body.reason, actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=_purchase_response(purchase_row))


@router.patch(
    "/platform/listings/{listing_id}/commission",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def change_commission(
    listing_id: str,
    body: CommissionRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    from decimal import Decimal, InvalidOperation

    listing = await db.get(MarketplaceListing, listing_id)
    if listing is None:
        raise AppError("LISTING_INVALID", "Listing not found", 404)
    try:
        pct = Decimal(body.platform_commission_pct)
    except InvalidOperation as exc:
        raise AppError("VALIDATION_ERROR", "Invalid percentage", 422) from exc
    if not pct.is_finite() or pct < 0 or pct > 100:
        raise AppError("VALIDATION_ERROR", "Commission must be 0-100", 422)
    before = str(listing.platform_commission_pct)
    listing.platform_commission_pct = pct
    await record_audit(
        db,
        actor=make_actor(request, user),
        action="listing.commission_changed",
        target_type="listing",
        target_id=listing.id,
        tenant_id=listing.seller_tenant_id,
        before={"pct": before},
        after={"pct": str(pct)},
    )
    await db.commit()
    return DataResponse(data=_listing_response(listing))

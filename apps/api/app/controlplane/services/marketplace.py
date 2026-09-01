"""Marketplace: listings, purchases with frozen economics, license grants,
install gate (ADR-014 §8)."""

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.marketplace import (
    LICENSE_SCOPES,
    OFFER_TYPES,
    PRODUCT_TYPES,
    LicenseGrant,
    MarketplaceListing,
    MarketplacePurchase,
)
from app.controlplane.models.outbox import enqueue
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services.audit import Actor, record_audit
from app.exceptions import AppError

log = structlog.get_logger()


def _now() -> datetime:
    return datetime.now(UTC)


def split_economics(
    amount_minor: int,
    commission_pct: Decimal,
    partner_rate: Decimal | None,
) -> tuple[int, int, int]:
    """(platform_fee, seller_share, partner_share). Partner share comes out
    of the platform fee. Pure — unit-tested with exact numbers."""
    fee = int(
        (Decimal(amount_minor) * commission_pct / 100).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )
    seller = amount_minor - fee
    partner = 0
    if partner_rate is not None:
        partner = int(
            (Decimal(amount_minor) * partner_rate / 100).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        partner = min(partner, fee)  # never exceeds the platform's cut
    return fee, seller, partner


async def _load_product(db: AsyncSession, product_type: str, product_id: str):
    """Returns (product, owner_org_id, status_value, visibility_value)."""
    if product_type == "skill_pack":
        from app.models.skill_pack import SkillPack

        pack = await db.get(SkillPack, product_id)
        if pack is None:
            return None
        return pack, pack.owner_org_id, pack.status.value, pack.visibility.value
    if product_type == "workflow_pack":
        from app.models.workflow_pack import WorkflowPack

        pack = await db.get(WorkflowPack, product_id)
        if pack is None:
            return None
        return pack, pack.owner_org_id, pack.status.value, pack.visibility.value
    if product_type == "learning_path":
        from app.models.learning_path import LearningPath

        path = await db.get(LearningPath, product_id)
        if path is None:
            return None
        return path, path.org_id, "published", "unlisted"
    return None


# ── Listings ─────────────────────────────────────────────────


async def create_listing(
    db: AsyncSession,
    *,
    seller_org_id: str,
    product_type: str,
    product_id: str,
    offer_type: str,
    price_minor: int | None,
    currency: str | None,
    license_scope: str,
    seat_limit: int | None,
    upgrade_policy: str,
    included_plan_keys: list,
    bill_via_invoice: bool,
    actor: Actor,
) -> MarketplaceListing:
    if product_type not in PRODUCT_TYPES:
        raise AppError("LISTING_INVALID", f"Unknown product type '{product_type}'", 422)
    if offer_type not in OFFER_TYPES:
        raise AppError("LISTING_INVALID", f"Unknown offer type '{offer_type}'", 422)
    if license_scope not in LICENSE_SCOPES:
        raise AppError("LISTING_INVALID", f"Unknown license scope '{license_scope}'", 422)
    if offer_type in ("paid", "partner_only") and (not price_minor or not currency):
        raise AppError("LISTING_INVALID", "Paid listings need price and currency", 422)
    if license_scope == "seat_limited" and not seat_limit:
        raise AppError("LISTING_INVALID", "seat_limited listings need seat_limit", 422)

    loaded = await _load_product(db, product_type, product_id)
    if loaded is None:
        raise AppError("PACK_NOT_FOUND", "Product not found", 404)
    _product, owner_org_id, status_value, visibility_value = loaded
    if owner_org_id != seller_org_id:
        # Anti-enumeration: same code as missing
        raise AppError("PACK_NOT_FOUND", "Product not found", 404)
    if status_value != "published":
        raise AppError("LISTING_INVALID", "Only published products can be listed", 422)
    if offer_type in ("paid", "partner_only") and visibility_value == "private":
        raise AppError(
            "LISTING_INVALID",
            "Paid listings require public or unlisted visibility",
            422,
        )
    from app.controlplane.services.tenants import get_tenant_for_org

    tenant = await get_tenant_for_org(db, seller_org_id)
    dup = (
        await db.execute(
            select(MarketplaceListing.id)
            .where(
                MarketplaceListing.product_type == product_type,
                MarketplaceListing.product_id == product_id,
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if dup is not None:
        raise AppError("LISTING_INVALID", "Product already has a listing", 409)
    from app.config import settings

    listing = MarketplaceListing(
        product_type=product_type,
        product_id=product_id,
        seller_org_id=seller_org_id,
        seller_tenant_id=tenant.id,
        offer_type=offer_type,
        price_minor=price_minor,
        currency=currency,
        license_scope=license_scope,
        seat_limit=seat_limit,
        upgrade_policy=upgrade_policy,
        platform_commission_pct=Decimal(settings.platform_default_commission_pct),
        included_plan_keys=included_plan_keys,
        bill_via_invoice=bill_via_invoice,
        created_by=actor.user_id,
    )
    db.add(listing)
    await db.flush()
    return listing


# ── Purchase flow ────────────────────────────────────────────


async def _latest_major(db: AsyncSession, product_type: str, product_id: str) -> int | None:
    """Latest release major version at purchase time (major_locked gating)."""
    try:
        if product_type == "skill_pack":
            from app.models.skill_pack import SkillPackRelease as Rel

            versions = (
                (await db.execute(select(Rel.version).where(Rel.pack_id == product_id)))
                .scalars()
                .all()
            )
        elif product_type == "workflow_pack":
            from app.models.workflow_pack import WorkflowPackRelease as Rel

            versions = (
                (await db.execute(select(Rel.version).where(Rel.pack_id == product_id)))
                .scalars()
                .all()
            )
        else:
            return None
        majors = []
        for v in versions:
            try:
                majors.append(int(str(v).split(".")[0]))
            except ValueError:
                continue
        return max(majors) if majors else None
    except Exception:  # noqa: BLE001 — best-effort metadata
        return None


async def create_purchase(
    db: AsyncSession,
    *,
    listing_id: str,
    buyer_org_id: str,
    purchaser: Actor,
    payment_method: str,
    idempotency_key: str | None,
) -> MarketplacePurchase:
    """Creates the pending purchase with FROZEN economics. Grant attribution
    comes ONLY from this row — request params can never plant a foreign
    tenant (IDOR-proof by construction)."""
    from app.controlplane.services.tenants import get_tenant_for_org

    listing = await db.get(MarketplaceListing, listing_id)
    if listing is None or listing.status != "active":
        raise AppError("LISTING_NOT_PURCHASABLE", "Listing is not available", 409)
    if listing.offer_type not in ("paid", "partner_only"):
        raise AppError("LISTING_NOT_PURCHASABLE", "Listing is not purchasable", 409)
    buyer_tenant = await get_tenant_for_org(db, buyer_org_id)
    if buyer_tenant.id == listing.seller_tenant_id:
        raise AppError("ALREADY_OWNED", "Cannot purchase your own product", 409)
    if listing.offer_type == "partner_only" and buyer_tenant.partner_id is None:
        raise AppError(
            "LISTING_NOT_PURCHASABLE", "This listing is available to partner tenants only", 409
        )
    seller_tenant = await db.get(TenantAccount, listing.seller_tenant_id)
    # Suspended/cancelled/archived sellers can't sell (§8.9); TRIAL can —
    # listing creation already gates on the paid_marketplace entitlement.
    if seller_tenant is None or seller_tenant.status not in (
        TenantStatus.ACTIVE,
        TenantStatus.PAST_DUE,
        TenantStatus.TRIAL,
    ):
        raise AppError("LISTING_NOT_PURCHASABLE", "Seller is not currently active", 409)
    covering = await _find_covering_grant(
        db, listing.product_type, listing.product_id, buyer_tenant.id, buyer_org_id
    )
    if covering is not None:
        raise AppError("ALREADY_LICENSED", "You already hold a license for this product", 409)
    if idempotency_key:
        existing = (
            await db.execute(
                select(MarketplacePurchase).where(
                    MarketplacePurchase.idempotency_key == idempotency_key
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing

    # Currency conversion into the buyer's currency (FX snapshot)
    amount = listing.price_minor or 0
    currency = buyer_tenant.currency
    fx_snapshot = None
    if listing.currency != buyer_tenant.currency:
        from app.controlplane.services.rating import convert_minor, resolve_fx

        fx = await resolve_fx(db, listing.currency, buyer_tenant.currency, _now())
        if fx is None:
            raise AppError(
                "LISTING_NOT_PURCHASABLE",
                f"No exchange rate for {listing.currency}->{buyer_tenant.currency}",
                409,
            )
        rate, fx_snapshot = fx
        amount = convert_minor(amount, rate, listing.currency, buyer_tenant.currency)

    # Frozen economics: commission + resolved rev-share rules AT THIS INSTANT
    from app.controlplane.services.revenue_share import _resolve_rule, _rule_snapshot

    seller_rule = await _resolve_rule(
        db,
        beneficiary_type="seller_org",
        partner_id=None,
        revenue_types=["marketplace"],
        at=_now(),
        tenant_id=listing.seller_tenant_id,
        listing_id=listing.id,
    )
    partner_rule = None
    if buyer_tenant.partner_id:
        partner_rule = await _resolve_rule(
            db,
            beneficiary_type="partner",
            partner_id=buyer_tenant.partner_id,
            revenue_types=["marketplace"],
            at=_now(),
            tenant_id=buyer_tenant.id,
            listing_id=listing.id,
        )
    fee, seller_share, partner_share = split_economics(
        amount,
        listing.platform_commission_pct,
        partner_rule.rate if partner_rule else None,
    )
    # A seller-specific rule overrides the default (amount − fee) split.
    # R56[25]: the override must REBALANCE the whole split, not just replace
    # seller_share — otherwise fee stays at the commission cut and
    # fee + seller + partner can exceed the amount collected (e.g. 90% seller
    # rule on a 20% commission distributed 125% of gross). The invariant is
    # seller + fee == amount with partner paid OUT of the fee; a seller rule
    # simply moves the seller/fee boundary.
    if seller_rule is not None and seller_rule.rate is not None:
        seller_share = min(
            int(
                (Decimal(amount) * seller_rule.rate / 100).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            ),
            amount,
        )
        fee = amount - seller_share
        partner_share = min(partner_share, fee)  # partner still capped at the fee
    purchase = MarketplacePurchase(
        listing_id=listing.id,
        buyer_tenant_id=buyer_tenant.id,
        buyer_org_id=buyer_org_id,
        purchaser_user_id=purchaser.user_id,
        amount_minor=amount,
        currency=currency,
        platform_fee_minor=fee,
        seller_share_minor=seller_share,
        partner_share_minor=partner_share,
        payment_method=payment_method,
        idempotency_key=idempotency_key,
        economics_snapshot={
            "commission_pct": str(listing.platform_commission_pct),
            "amount_minor": amount,
            "currency": currency,
            "platform_fee_minor": fee,
            "seller_share_minor": seller_share,
            "partner_share_minor": partner_share,
            "seller_org_id": listing.seller_org_id,
            "partner_id": buyer_tenant.partner_id,
            "seller_rule_snapshot": _rule_snapshot(seller_rule) if seller_rule else None,
            "partner_rule_snapshot": _rule_snapshot(partner_rule) if partner_rule else None,
            "fx_rate_snapshot": fx_snapshot,
            "listing_price_minor": listing.price_minor,
            "listing_currency": listing.currency,
            "purchased_major": await _latest_major(db, listing.product_type, listing.product_id),
        },
    )
    db.add(purchase)
    await db.flush()
    return purchase


async def mark_purchase_paid(
    db: AsyncSession,
    *,
    purchase_id: str,
    payment_ref: str | None,
    actor: Actor,
) -> MarketplacePurchase:
    """Guarded pending→paid; creates the license grant, emits the
    content_license usage event and the purchase.paid outbox message."""
    result = await db.execute(
        update(MarketplacePurchase)
        .where(
            MarketplacePurchase.id == purchase_id,
            MarketplacePurchase.status == "pending",
        )
        .values(status="paid", payment_ref=payment_ref)
    )
    if not result.rowcount:
        existing = await db.get(MarketplacePurchase, purchase_id)
        if existing is None:
            raise AppError("PURCHASE_STATUS_CONFLICT", "Purchase not found", 404)
        return existing  # already paid — idempotent for webhook replays
    purchase = await db.get(MarketplacePurchase, purchase_id)
    listing = await db.get(MarketplaceListing, purchase.listing_id)
    grant = LicenseGrant(
        listing_id=listing.id,
        product_type=listing.product_type,
        product_id=listing.product_id,
        # Attribution ONLY from the purchase row (IDOR-proof)
        tenant_id=purchase.buyer_tenant_id,
        org_id=purchase.buyer_org_id if listing.license_scope != "tenant" else None,
        scope=listing.license_scope,
        seat_limit=listing.seat_limit,
        source="purchase",
        purchase_id=purchase.id,
        purchased_major=(purchase.economics_snapshot or {}).get("purchased_major"),
    )
    db.add(grant)
    from app.controlplane.services.metering import emit_usage

    await emit_usage(
        db,
        tenant_id=purchase.buyer_tenant_id,
        org_id=purchase.buyer_org_id,
        usage_type="content_license",
        quantity=1,
        occurred_at=_now(),
        source="manual",
        idempotency_key=f"license:{purchase.id}",
        metadata={"listing_id": listing.id, "purchase_id": purchase.id},
    )
    enqueue(db, "purchase.paid", {"purchase_id": purchase.id})
    await db.flush()
    return purchase


async def refund_purchase(
    db: AsyncSession, purchase_id: str, *, reason: str, actor: Actor
) -> MarketplacePurchase:
    """paid→refunded; revokes the license; refunds credit payments; negative
    rev-share adjustments via outbox. Installed content is NEVER touched
    (issue §27 — revocation only blocks new installs/upgrades)."""
    result = await db.execute(
        update(MarketplacePurchase)
        .where(MarketplacePurchase.id == purchase_id, MarketplacePurchase.status == "paid")
        .values(status="refunded", refund_reason=reason)
    )
    if not result.rowcount:
        raise AppError("PURCHASE_STATUS_CONFLICT", "Purchase is not in a refundable state", 409)
    purchase = await db.get(MarketplacePurchase, purchase_id)
    await db.execute(
        update(LicenseGrant)
        .where(LicenseGrant.purchase_id == purchase.id, LicenseGrant.status == "active")
        .values(status="revoked", revoked_at=_now(), revoke_reason=f"refund: {reason}")
    )
    if purchase.payment_method == "credit":
        from app.controlplane.services import credits as credit_svc

        await credit_svc.refund(
            db,
            purchase.buyer_tenant_id,
            purchase.currency,
            purchase.amount_minor,
            reference_type="purchase",
            reference_id=purchase.id,
            reason=reason,
            actor=actor,
            idempotency_key=f"refund:{purchase.id}",
        )
    enqueue(db, "purchase.refunded", {"purchase_id": purchase.id})
    await record_audit(
        db,
        actor=actor,
        action="purchase.refunded",
        target_type="purchase",
        target_id=purchase.id,
        tenant_id=purchase.buyer_tenant_id,
        reason=reason,
        after={"amount_minor": purchase.amount_minor},
    )
    await db.flush()
    return purchase


# ── License gate (facade.check_install_license) ──────────────


async def _find_covering_grant(
    db: AsyncSession,
    product_type: str,
    product_id: str,
    tenant_id: str,
    org_id: str,
) -> LicenseGrant | None:
    grants = (
        (
            await db.execute(
                select(LicenseGrant).where(
                    LicenseGrant.product_type == product_type,
                    LicenseGrant.product_id == product_id,
                    LicenseGrant.tenant_id == tenant_id,
                    LicenseGrant.status == "active",
                )
            )
        )
        .scalars()
        .all()
    )
    now = _now()
    for grant in grants:
        if grant.expires_at is not None and grant.expires_at <= now:
            continue
        if grant.scope == "tenant":
            return grant
        if grant.scope in ("organization", "seat_limited", "cohort") and (
            grant.org_id == org_id or grant.org_id is None
        ):
            return grant
    return None


async def check_install_license(db: AsyncSession, product_type: str, product_id: str, org) -> None:
    """Install gate (wired into installation services + upgrade paths).

    free/no-listing → pass; own product → pass; private → uniform 404;
    included_with_plan → plan-key check + lazy grant; paid/partner_only →
    covering active grant required (seat occupancy approximated by org
    active-student count — ADR decision)."""
    listing = (
        await db.execute(
            select(MarketplaceListing).where(
                MarketplaceListing.product_type == product_type,
                MarketplaceListing.product_id == product_id,
                MarketplaceListing.status == "active",
            )
        )
    ).scalar_one_or_none()
    if listing is None or listing.offer_type == "free":
        return
    from app.controlplane.services.tenants import get_tenant_for_org

    tenant = await get_tenant_for_org(db, org.id)
    if tenant.id == listing.seller_tenant_id:
        return  # own product
    if listing.offer_type == "private":
        raise AppError("PACK_NOT_FOUND", "Pack not found", 404)  # anti-enumeration
    if listing.offer_type == "included_with_plan":
        from app.controlplane.services.entitlements import get_effective

        eff = await get_effective(db, tenant)
        if eff.plan_key in (listing.included_plan_keys or []):
            existing = await _find_covering_grant(db, product_type, product_id, tenant.id, org.id)
            if existing is None:
                db.add(
                    LicenseGrant(
                        listing_id=listing.id,
                        product_type=product_type,
                        product_id=product_id,
                        tenant_id=tenant.id,
                        org_id=org.id,
                        scope="organization",
                        source="plan_included",
                    )
                )
                await db.flush()
            return
        raise AppError(
            "LICENSE_REQUIRED",
            "This content is included with a higher plan",
            403,
        )
    # paid | partner_only
    grant = await _find_covering_grant(db, product_type, product_id, tenant.id, org.id)
    if grant is None:
        raise AppError(
            "LICENSE_REQUIRED",
            "A license is required to install this content",
            403,
        )
    if grant.scope == "seat_limited" and grant.seat_limit:
        from sqlalchemy import func as _f

        from app.models.organization import MemberStatus, OrgMember, OrgRole

        occupancy = (
            await db.execute(
                select(_f.count(_f.distinct(OrgMember.user_id))).where(
                    OrgMember.org_id == org.id,
                    OrgMember.status == MemberStatus.ACTIVE,
                    OrgMember.role == OrgRole.STUDENT,
                )
            )
        ).scalar_one()
        if occupancy > grant.seat_limit:
            raise AppError(
                "SEAT_LIMIT_EXCEEDED",
                f"License covers {grant.seat_limit} seats; organization has {occupancy}",
                403,
            )


async def check_upgrade_license(
    db: AsyncSession, product_type: str, product_id: str, org, target_version: str
) -> None:
    """Upgrade extra: major_locked grants block newer majors than purchased."""
    await check_install_license(db, product_type, product_id, org)
    listing = (
        await db.execute(
            select(MarketplaceListing).where(
                MarketplaceListing.product_type == product_type,
                MarketplaceListing.product_id == product_id,
                MarketplaceListing.status == "active",
                MarketplaceListing.upgrade_policy == "major_locked",
            )
        )
    ).scalar_one_or_none()
    if listing is None:
        return
    from app.controlplane.services.tenants import get_tenant_for_org

    tenant = await get_tenant_for_org(db, org.id)
    if tenant.id == listing.seller_tenant_id:
        return
    grant = await _find_covering_grant(db, product_type, product_id, tenant.id, org.id)
    if grant is None or grant.purchased_major is None:
        return
    try:
        target_major = int(str(target_version).split(".")[0])
    except ValueError:
        return
    if target_major > grant.purchased_major:
        raise AppError(
            "LICENSE_UPGRADE_REQUIRED",
            f"Your license covers major version {grant.purchased_major}; "
            f"version {target_version} requires a new purchase",
            403,
        )


# ── Manual grants / revocation ───────────────────────────────


async def manual_grant(
    db: AsyncSession,
    *,
    product_type: str,
    product_id: str,
    tenant_id: str,
    scope: str,
    org_id: str | None,
    expires_at: datetime | None,
    actor: Actor,
) -> LicenseGrant:
    if product_type not in PRODUCT_TYPES or scope not in LICENSE_SCOPES:
        raise AppError("LISTING_INVALID", "Invalid product type or scope", 422)
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    grant = LicenseGrant(
        product_type=product_type,
        product_id=product_id,
        tenant_id=tenant_id,
        org_id=org_id,
        scope=scope,
        source="manual_grant",
        granted_by=actor.user_id,
        expires_at=expires_at,
    )
    db.add(grant)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="license.granted_manually",
        target_type="license_grant",
        target_id=grant.id,
        tenant_id=tenant_id,
        after={"product_type": product_type, "product_id": product_id, "scope": scope},
    )
    return grant


async def revoke_grant(
    db: AsyncSession, grant_id: str, *, reason: str, actor: Actor
) -> LicenseGrant:
    grant = await db.get(LicenseGrant, grant_id)
    if grant is None:
        raise AppError("LICENSE_NOT_FOUND", "License grant not found", 404)
    if grant.status != "active":
        raise AppError("PURCHASE_STATUS_CONFLICT", "Grant is not active", 409)
    grant.status = "revoked"
    grant.revoked_at = _now()
    grant.revoke_reason = reason
    await record_audit(
        db,
        actor=actor,
        action="license.revoked",
        target_type="license_grant",
        target_id=grant.id,
        tenant_id=grant.tenant_id,
        reason=reason,
    )
    await db.flush()
    return grant

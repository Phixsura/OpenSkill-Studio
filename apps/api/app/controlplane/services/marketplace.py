"""Marketplace: listings, purchases with frozen economics, license grants,
install gate (ADR-014 §8)."""

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

import structlog
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
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
        # R44[19]: report the path's REAL status — hardcoding "published" made
        # create_listing's published-only gate vacuous (DRAFT/archived paths
        # were listable and purchasable). Learning paths have no visibility
        # dimension; "unlisted" remains the sale-compatible constant.
        return path, path.org_id, path.status.value, "unlisted"
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
    # R135: the mirror direction — a seat_limit on any OTHER scope is dead
    # data (enforce_seat_limit only fires on scope == 'seat_limited'), so a
    # seller pricing a "10-seat team license" on scope=organization silently
    # sold unlimited seats. Reject the contradiction up front (R44[20] fixed
    # the same mirror for manual grants).
    if license_scope != "seat_limited" and seat_limit is not None:
        raise AppError(
            "LISTING_INVALID",
            "seat_limit is only valid with license_scope='seat_limited'",
            422,
        )

    loaded = await _load_product(db, product_type, product_id)
    if loaded is None:
        raise AppError("PACK_NOT_FOUND", "Product not found", 404)
    _product, owner_org_id, status_value, visibility_value = loaded
    if owner_org_id != seller_org_id:
        # Anti-enumeration: same code as missing
        raise AppError("PACK_NOT_FOUND", "Product not found", 404)
    # R113[H0]: a learning path installed from someone else's paid listing is
    # an org-owned COPY (org_id == buyer) — ownership alone let the buyer
    # re-list purchased content for sale (H1 redistribution class for paths;
    # skills/templates have the same gate via origin_pack_id).
    if product_type == "learning_path" and getattr(_product, "origin_listing_id", None):
        origin = await db.get(MarketplaceListing, _product.origin_listing_id)
        if (
            origin is not None
            and origin.offer_type in ("paid", "partner_only")
            and origin.seller_org_id != seller_org_id
        ):
            raise AppError(
                "LICENSED_CONTENT_NOT_REDISTRIBUTABLE",
                "This learning path was installed from a paid listing and "
                "cannot be re-listed for sale",
                403,
            )
    # R132 ([F11]): manual-grant copies carry ONLY origin_source_path_id (no
    # listing) — the listing-keyed gate above missed them, so a grant-redeemed
    # copy of ANOTHER org's path was re-listable for sale. Block listing any
    # copy whose source path is owned by a different org.
    if product_type == "learning_path" and getattr(_product, "origin_source_path_id", None):
        from app.models.learning_path import LearningPath as LearningPathModel

        src = await db.get(LearningPathModel, _product.origin_source_path_id)
        if src is not None and src.org_id != seller_org_id:
            raise AppError(
                "LICENSED_CONTENT_NOT_REDISTRIBUTABLE",
                "This learning path is an installed copy of another "
                "organization's content and cannot be re-listed for sale",
                403,
            )
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
        raise AppError("LISTING_EXISTS", "Product already has a listing", 409)
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
    # R86[M8]: nothing delists a listing when its product dies — buyers paid
    # for archived (uninstallable) packs. Re-check product liveness with the
    # same rules the install gate applies.
    product = await _load_product(db, listing.product_type, listing.product_id)
    if product is None:
        raise AppError("LISTING_NOT_PURCHASABLE", "Listing is not available", 409)
    _p, _owner, p_status, p_visibility = product
    if p_status != "published" or p_visibility not in ("public", "unlisted"):
        raise AppError("LISTING_NOT_PURCHASABLE", "Listing is not available", 409)
    buyer_tenant = await get_tenant_for_org(db, buyer_org_id)
    if buyer_tenant.id == listing.seller_tenant_id:
        raise AppError("ALREADY_OWNED", "Cannot purchase your own product", 409)
    if listing.offer_type == "partner_only":
        # R113[M13]: partner attribution alone isn't partnership — a
        # suspended/terminated partner's tenants kept buying partner-only
        # listings (the partner row stays for attribution history). The
        # PARTNER must be currently active.
        partner_active = False
        if buyer_tenant.partner_id is not None:
            from app.controlplane.models.partner import Partner

            partner = await db.get(Partner, buyer_tenant.partner_id)
            partner_active = partner is not None and partner.status == "active"
        if not partner_active:
            raise AppError(
                "LISTING_NOT_PURCHASABLE", "This listing is available to partner tenants only", 409
            )
    # R44[22]: invoice billing is opt-in PER LISTING — the seller flags
    # bill_via_invoice; buyers of other listings must pay up front.
    if payment_method == "invoice" and not listing.bill_via_invoice:
        raise AppError(
            "LISTING_NOT_PURCHASABLE",
            "This listing does not support invoice billing",
            409,
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
    # R132 ([F0], completes R131's scope-width rule): a NARROWER grant must
    # not block purchasing the WIDER entitlement — an org-scoped grant holder
    # upgrading to a tenant-wide license 409'd here before checkout ever
    # started. R133 ([F10]): evaluate width over ALL covering grants — the
    # single-widest answer let an expiring tenant trial (wide scope, fails
    # duration) shadow a perpetual org grant that fully covers this listing,
    # allowing a redundant charge.
    all_covering = await _covering_grants(
        db, listing.product_type, listing.product_id, buyer_tenant.id, buyer_org_id
    )
    # R135: major axis — resolve the current latest major once so a
    # major_locked grant pinned below it does NOT block the upgrade purchase.
    _lm = (
        await _latest_major(db, listing.product_type, listing.product_id)
        if listing.upgrade_policy == "major_locked"
        else None
    )
    if any(grant_covers_listing_width(g, listing, latest_major=_lm) for g in all_covering):
        raise AppError("ALREADY_LICENSED", "You already hold a license for this product", 409)
    # R44[17]: the grant precheck only sees PAID purchases (grants are created
    # at mark_paid) — nothing stopped a second purchase while the first was
    # still pending (double-click, checkout retry), each independently payable.
    # A pending purchase for the same (listing, buyer tenant) is returned
    # as-is: the buyer resumes it instead of opening a parallel charge.
    # R123[H8]: resume only a SAME-payment-method pending purchase, and lock
    # it — resuming a pending CHECKOUT purchase into the credit branch raced
    # the Stripe webhook's pending→paid flip: the webhook collected the card
    # while the endpoint debited credits against the same purchase (double
    # charge, no reversal). FOR UPDATE serializes against the webhook; the
    # method filter stops cross-method resumes entirely (a buyer switching
    # methods gets a fresh purchase; the stale pending one expires unpaid).
    pending = (
        await db.execute(
            select(MarketplacePurchase)
            .where(
                MarketplacePurchase.listing_id == listing.id,
                MarketplacePurchase.buyer_tenant_id == buyer_tenant.id,
                MarketplacePurchase.status == "pending",
                MarketplacePurchase.payment_method == payment_method,
            )
            .order_by(MarketplacePurchase.created_at.desc())
            .limit(1)
            .with_for_update()
        )
    ).scalar_one_or_none()
    if pending is not None:
        return pending
    if idempotency_key:
        # R72[2]: scope the idempotency lookup to the BUYER — client-supplied
        # keys share one table; an unscoped match returned ANOTHER tenant's
        # purchase (cross-tenant data leak, and the credit path then debited
        # the wrong tenant's balance).
        # R101[H0]: only LIVE purchases resume through the key — a refunded or
        # failed purchase matching the (stable) client key returned the dead
        # row as "success", permanently blocking re-purchase after a refund.
        existing = (
            await db.execute(
                select(MarketplacePurchase).where(
                    MarketplacePurchase.buyer_tenant_id == buyer_tenant.id,
                    MarketplacePurchase.idempotency_key == idempotency_key,
                    MarketplacePurchase.status.in_(("pending", "paid")),
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing
        # A DEAD purchase (refunded/failed) still holds the unique key — free
        # it (history row keeps a suffixed copy) so the fresh purchase can
        # reuse the client's stable key instead of 500ing on the index.
        from ulid import ULID

        await db.execute(
            update(MarketplacePurchase)
            .where(
                MarketplacePurchase.buyer_tenant_id == buyer_tenant.id,
                MarketplacePurchase.idempotency_key == idempotency_key,
                MarketplacePurchase.status.in_(("refunded", "failed")),
            )
            .values(idempotency_key=idempotency_key[:90] + ":r:" + str(ULID()))
        )

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
    try:
        # R113[M14]: two concurrent purchases with the same idempotency key
        # both pass the pre-SELECT (R72[2]) and race on uq_cp_purchase_idem —
        # the loser died as an unhandled 500 and poisoned the session (M35).
        # SAVEPOINT-isolate the insert (add INSIDE the savepoint so the
        # rollback expunges the dead row — the recover path continues and the
        # caller commits); on conflict resume the winner's LIVE row exactly
        # like the pre-check would have.
        async with db.begin_nested():
            db.add(purchase)
            await db.flush()
    except IntegrityError:
        existing = (
            await db.execute(
                select(MarketplacePurchase).where(
                    MarketplacePurchase.buyer_tenant_id == buyer_tenant.id,
                    MarketplacePurchase.idempotency_key == idempotency_key,
                    MarketplacePurchase.status.in_(("pending", "paid")),
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing
        raise AppError(
            "PURCHASE_STATUS_CONFLICT", "Concurrent purchase with this idempotency key", 409
        ) from None
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
            raise AppError("PURCHASE_NOT_FOUND", "Purchase not found", 404)
        return existing  # already paid — idempotent for webhook replays
    purchase = await db.get(MarketplacePurchase, purchase_id)
    listing = await db.get(MarketplaceListing, purchase.listing_id)
    # R129[H0]: a stale pending CHECKOUT purchase can complete via the Stripe
    # webhook AFTER the buyer already licensed the product another way (a
    # credit purchase for the same listing). The create_purchase ALREADY_
    # LICENSED precheck does not cover this webhook-driven path. Skip minting a
    # duplicate active grant for the same (tenant/org, product) — the payment
    # is recorded (paid) so ops can refund the redundant charge; the license
    # already exists.
    scope_org = purchase.buyer_org_id if listing.license_scope != "tenant" else None
    # R130 (rework of R129[H0]): use the canonical covering-grant helper —
    # the ad-hoc exact-shape query (a) crashed with MultipleResultsFound on
    # duplicate active grants (real: pre-H0 mints, double manual grants),
    # (b) ignored expires_at, so a date-expired grant suppressed the mint for
    # a genuinely PAID renewal (money taken, no license), and (c) missed a
    # covering tenant-wide grant for an org-scoped listing (the original H0
    # double-mint surviving for scope-superset shapes). _find_covering_grant
    # applies expiry + scope semantics; a covered buyer = true duplicate.
    # R131 ([F9]) / R132 ([F1]/[F2]): the existing grant must cover the FULL
    # WIDTH of the purchase — scope, duration, seat capacity — or the buyer
    # paid for more than they hold. R133 ([F10]): evaluate ALL covering
    # grants (single-widest let an expiring wide trial shadow a perpetual
    # covering grant). Shared helper keeps this in lockstep with the
    # create_purchase precheck.
    _all_covering = await _covering_grants(
        db,
        listing.product_type,
        listing.product_id,
        purchase.buyer_tenant_id,
        purchase.buyer_org_id,
    )
    _lm_paid = (
        await _latest_major(db, listing.product_type, listing.product_id)
        if listing.upgrade_policy == "major_locked"
        else None
    )
    existing_grant = next(
        (g for g in _all_covering if grant_covers_listing_width(g, listing, latest_major=_lm_paid)),
        None,
    )
    if existing_grant is None:
        grant = LicenseGrant(
            listing_id=listing.id,
            product_type=listing.product_type,
            product_id=listing.product_id,
            # Attribution ONLY from the purchase row (IDOR-proof)
            tenant_id=purchase.buyer_tenant_id,
            org_id=scope_org,
            scope=listing.license_scope,
            seat_limit=listing.seat_limit,
            source="purchase",
            purchase_id=purchase.id,
            purchased_major=(purchase.economics_snapshot or {}).get("purchased_major"),
        )
        db.add(grant)
    else:
        log.warning(
            "cp_purchase_paid_duplicate_license",
            purchase_id=purchase.id,
            existing_grant_id=existing_grant.id,
            detail="paid purchase for an already-licensed product — refund candidate",
        )
    # R130: only meter content_license when a grant was actually DELIVERED —
    # the H0 skip branch still emitted the event, so a tenant whose price
    # policy rates content_license was billed a usage line for a license that
    # never existed (and refund_purchase never reverses usage events).
    if existing_grant is None:
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
    # R60[42]: mark-paid delivers a license and triggers rev-share accrual —
    # the actor (buyer via credit/invoice, SYSTEM via webhook, billing_admin
    # via /platform/purchases/{id}/mark-paid) must be reconstructible.
    await record_audit(
        db,
        actor=actor,
        action="purchase.marked_paid",
        target_type="purchase",
        target_id=purchase.id,
        tenant_id=purchase.buyer_tenant_id,
        after={"amount_minor": purchase.amount_minor, "currency": purchase.currency},
    )
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
    # R80[3]: money must come back for EVERY payment method — the old branch
    # refunded only credit-paid purchases; checkout (real card charge) and
    # invoice-billed purchases were "refunded" in name only (license revoked,
    # money kept). v1 has no provider-side refund API, so non-credit payments
    # are returned as PLATFORM CREDIT to the buyer's balance (spendable on
    # anything; ADR-noted v1 policy — provider-native refunds are a later
    # adapter capability). Skip only invoice-billed purchases whose license
    # line was never invoiced (nothing was ever charged) — mark_purchase_paid
    # sets invoice_id when the line lands.
    from app.controlplane.services import credits as credit_svc

    charged = purchase.payment_method != "invoice"
    if purchase.payment_method == "invoice" and purchase.invoice_id is not None:
        # R88[11]: an invoiced-but-UNPAID purchase (license line on a still-
        # open invoice) has collected NOTHING — refunding it minted spendable
        # credit for money never received (buy → invoice closes → refund →
        # free credit; the debt stayed on the open invoice too). Money only
        # comes back when the invoice actually collected: status 'paid'.
        # For open invoices the correction is a credit NOTE on that invoice
        # (reduces the debt), issued by ops alongside this refund.
        from app.controlplane.models.billing import Invoice as _Inv

        inv_status = (
            await db.execute(select(_Inv.status).where(_Inv.id == purchase.invoice_id))
        ).scalar_one_or_none()
        charged = inv_status == "paid"
        if not charged:
            log.warning(
                "cp_refund_invoice_not_collected",
                purchase_id=purchase.id,
                invoice_id=purchase.invoice_id,
                invoice_status=inv_status,
            )
    if charged:
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
    else:
        # Nothing collected (un-invoiced pending charge, or open invoice) —
        # no ledger refund; the status flip stops future billing.
        log.info("cp_refund_uncharged_invoice_purchase", purchase_id=purchase.id)
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


def _grant_rank(grant: LicenseGrant) -> tuple:
    """Width order: tenant > organization/cohort > seat_limited; perpetual >
    expiring; roomier seat cap on ties (R132[F3]/[20])."""
    scope_rank = 2 if grant.scope == "tenant" else (0 if grant.scope == "seat_limited" else 1)
    return (scope_rank, 1 if grant.expires_at is None else 0, grant.seat_limit or 0)


async def _covering_grants(
    db: AsyncSession,
    product_type: str,
    product_id: str,
    tenant_id: str,
    org_id: str,
) -> list[LicenseGrant]:
    """ALL live covering grants, widest first (R133 [F10]/[F11]: consumers
    that ask 'is the buyer already licensed for X width?' or 'what major did
    the buyer PURCHASE?' must see every covering grant — the single-widest
    answer let an expiring tenant trial shadow a perpetual org purchase)."""
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
    covering = []
    for grant in grants:
        if grant.expires_at is not None and grant.expires_at <= now:
            continue
        # 'cohort' scope enforces at the ORG boundary by design (ADR-014 §8.4:
        # cohort narrowing lives at the assignment layer — usage events don't
        # carry a cohort dim in v1). grant.cohort_id records the intended
        # cohort for that layer; it does not narrow the install gate.
        covers = grant.scope == "tenant" or (
            grant.scope in ("organization", "seat_limited", "cohort")
            and (grant.org_id == org_id or grant.org_id is None)
        )
        if covers:
            covering.append(grant)
    covering.sort(key=_grant_rank, reverse=True)
    return covering


async def _find_covering_grant(
    db: AsyncSession,
    product_type: str,
    product_id: str,
    tenant_id: str,
    org_id: str,
) -> LicenseGrant | None:
    """The single WIDEST covering grant (install-gate semantics — the widest
    entitlement governs seat caps etc.). Width-comparison consumers should
    use _covering_grants and evaluate ALL of them."""
    covering = await _covering_grants(db, product_type, product_id, tenant_id, org_id)
    return covering[0] if covering else None


def grant_covers_listing_width(
    grant: LicenseGrant, listing: MarketplaceListing, *, latest_major: int | None = None
) -> bool:
    """R132: does an existing grant cover the WIDTH of what a listing sells?

    A purchase mints a perpetual grant at the listing's scope/seat cap — an
    existing grant only makes that purchase redundant when it is at least as
    wide on every axis: scope (tenant > org/cohort/seat_limited), duration
    (perpetual vs expiring), seat capacity, and — under major_locked — the
    MAJOR VERSION axis (R135). Shared by the create_purchase ALREADY_LICENSED
    precheck and the mark_purchase_paid mint guard so the two never diverge
    (the R129→R131 divergence class)."""
    if listing.license_scope == "tenant" and grant.scope != "tenant":
        return False
    if grant.expires_at is not None:
        return False
    # R135: under major_locked, a purchase today sells access UP TO the
    # CURRENT latest major. A paid grant pinned below it does not cover that
    # width — without this axis the upgrade gate demanded a new purchase
    # (LICENSE_UPGRADE_REQUIRED) that this very check then 409'd
    # (ALREADY_LICENSED): self-serve upgrades were impossible by construction.
    # purchased_major=None grants (manual/plan-included) are major-unlimited —
    # the upgrade gate binds only on paid majors — so they DO cover.
    if (
        listing.upgrade_policy == "major_locked"
        and latest_major is not None
        and grant.purchased_major is not None
        and grant.purchased_major < latest_major
    ):
        return False
    return not (
        grant.scope == "seat_limited"
        and (
            listing.license_scope != "seat_limited"
            or (grant.seat_limit or 0) < (listing.seat_limit or 0)
        )
    )


async def enforce_seat_limit(db: AsyncSession, grant: LicenseGrant, org_id: str) -> None:
    """R130[5]/R131: seat_limited occupancy gate — shared by the install gate
    AND the listing-less learning-path path (which bypasses
    check_install_license entirely, so the cap was silently unenforced there)."""
    if grant.scope == "seat_limited" and grant.seat_limit:
        from sqlalchemy import func as _f

        from app.models.organization import (
            MemberStatus,
            Organization,
            OrgMember,
            OrgRole,
            OrgStatus,
        )

        q = (
            select(_f.count(_f.distinct(OrgMember.user_id)))
            .select_from(OrgMember)
            .where(
                OrgMember.status == MemberStatus.ACTIVE,
                OrgMember.role == OrgRole.STUDENT,
            )
        )
        # R132 ([F12]): a grant narrowed to one org caps THAT org; a
        # tenant-wide seat_limited grant (org_id NULL) caps the TENANT's
        # total occupancy — per-installing-org counting let N orgs each
        # consume the full cap (N× the seats the seller sold).
        if grant.org_id is not None:
            q = q.where(OrgMember.org_id == org_id)
        else:
            q = q.join(Organization, Organization.id == OrgMember.org_id).where(
                Organization.tenant_id == grant.tenant_id,
                Organization.status != OrgStatus.ARCHIVED,
            )
        occupancy = (await db.execute(q)).scalar_one()
        if occupancy > grant.seat_limit:
            raise AppError(
                "SEAT_LIMIT_EXCEEDED",
                f"License covers {grant.seat_limit} seats; current occupancy is {occupancy}",
                403,
            )


async def check_install_license(
    db: AsyncSession,
    product_type: str,
    product_id: str,
    org,
    target_version: str | None = None,
) -> None:
    """Install gate (wired into installation services + upgrade paths).

    free/no-listing → pass; own product → pass; private → uniform 404;
    included_with_plan → plan-key check + lazy grant; paid/partner_only →
    covering active grant required (seat occupancy approximated by org
    active-student count — ADR decision).

    target_version (when the caller knows which release it will install) also
    enforces major_locked on FRESH installs — previously only /upgrade checked
    majors, so uninstall→reinstall (or a fresh install resolving the latest
    release) delivered any newer major on an old license (R44[18])."""
    # R44[16]: the gate must consider EVERY listing (any status except draft) —
    # delisting/suspending means "stop selling", not "give it away". The old
    # status=='active' filter made the gate return None after a delist, turning
    # paid content free and nullifying refund revocation (revoke the grant,
    # delist the listing → anyone reinstalls unlicensed).
    listing = (
        await db.execute(
            select(MarketplaceListing)
            .where(
                MarketplaceListing.product_type == product_type,
                MarketplaceListing.product_id == product_id,
                MarketplaceListing.status != "draft",
            )
            .order_by(MarketplaceListing.created_at.desc())
            .limit(1)
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
    covering = await _covering_grants(db, product_type, product_id, tenant.id, org.id)
    if not covering:
        raise AppError(
            "LICENSE_REQUIRED",
            "A license is required to install this content",
            403,
        )
    # R134 ([F8]): the install passes if ANY covering grant permits it under
    # its seat cap — the single-widest grant let a roomier-cap tenant-wide
    # grant (whose tenant-wide occupancy check can 403) shadow the buyer's
    # own org-scoped purchase grant that would allow the install. Try each;
    # only 403 when EVERY covering grant is over its cap.
    seat_error: AppError | None = None
    for _g in covering:
        try:
            await enforce_seat_limit(db, _g, org.id)
            seat_error = None
            break
        except AppError as _e:
            seat_error = _e
    if seat_error is not None:
        raise seat_error
    # R44[18]: major_locked applies to installs too, not just upgrades.
    # R133 ([F11]): the major bound comes from the PURCHASE grants, not the
    # widest grant — a purchased_major=NULL manual/trial grant shadowing the
    # paid grant silently unlocked all majors on a major-1 license. Bind on
    # the MAX purchased_major among covering grants (the buyer's highest paid
    # major); only when NO covering grant carries one (pure manual/trial
    # licensing) is the product major-unrestricted by ops intent.
    if target_version is not None and listing.upgrade_policy == "major_locked":
        purchased_majors = [
            g.purchased_major
            for g in await _covering_grants(db, product_type, product_id, tenant.id, org.id)
            if g.purchased_major is not None
        ]
        bound = max(purchased_majors) if purchased_majors else None
        try:
            target_major = int(str(target_version).split(".")[0])
        except ValueError:
            target_major = None
        if bound is not None and target_major is not None and target_major > bound:
            raise AppError(
                "LICENSE_UPGRADE_REQUIRED",
                f"Your license covers major version {bound}; "
                f"version {target_version} requires a new purchase",
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
                # R134 ([F7]): a delisted/suspended listing still binds its
                # major lock — "delisting means stop SELLING, not give away
                # newer majors" (R44[16], applied on the install side but
                # left active-only here). Exclude only 'draft'.
                MarketplaceListing.status != "draft",
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
    # R133 ([F11]): bind on the MAX purchased_major among ALL covering grants
    # — the widest grant may be a purchased_major=NULL trial that shadows the
    # paid grant (silently unlocking every major).
    purchased_majors = [
        g.purchased_major
        for g in await _covering_grants(db, product_type, product_id, tenant.id, org.id)
        if g.purchased_major is not None
    ]
    if not purchased_majors:
        return
    bound = max(purchased_majors)
    try:
        target_major = int(str(target_version).split(".")[0])
    except ValueError:
        return
    if target_major > bound:
        raise AppError(
            "LICENSE_UPGRADE_REQUIRED",
            f"Your license covers major version {bound}; "
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
    seat_limit: int | None = None,
) -> LicenseGrant:
    if product_type not in PRODUCT_TYPES or scope not in LICENSE_SCOPES:
        raise AppError("LISTING_INVALID", "Invalid product type or scope", 422)
    # R44[20]: a seat_limited grant with no limit silently skipped the seat
    # check (the gate is `if grant.seat_limit:`) — unlimited seats under a
    # scope that promises a cap. Require the limit when the scope demands it.
    if scope == "seat_limited" and (seat_limit is None or seat_limit <= 0):
        raise AppError("LISTING_INVALID", "seat_limited grants require a positive seat_limit", 422)
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    # R123[L7]: an org_id outside the tenant produced a grant the install gate
    # can never match (org.tenant_id != grant.tenant_id) — silently inert.
    if org_id is not None:
        from app.models.organization import Organization as _Org

        org_row = await db.get(_Org, org_id)
        if org_row is None or org_row.tenant_id != tenant_id:
            raise AppError("LISTING_INVALID", "org_id does not belong to the target tenant", 422)
    grant = LicenseGrant(
        product_type=product_type,
        product_id=product_id,
        tenant_id=tenant_id,
        org_id=org_id,
        scope=scope,
        seat_limit=seat_limit if scope == "seat_limited" else None,
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

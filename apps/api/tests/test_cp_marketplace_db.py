"""P8 DB tests: listings, purchase flow, install gate matrix, refunds,
commission snapshot isolation."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from ulid import ULID

from app.controlplane.models.marketplace import (
    LicenseGrant,
    MarketplaceListing,
)
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import credits as credit_svc
from app.controlplane.services import marketplace as market_svc
from app.controlplane.services.audit import Actor
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.organization import Organization
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack
from app.models.user import User, UserRole, UserStatus
from app.services.organization import OrgService


@pytest.fixture
async def db():
    from app.core.database import engine

    # R134 follow-up: a preceding file can leave pool connections bound to its
    # (now closed) event loop — the first checkout here then dies with
    # "Event loop is closed". Abandon any stale pool without touching the
    # dead-loop connections (close=False), then open fresh ones on this loop.
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_user(db) -> User:
    user = User(
        email=f"cp8-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP8",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_org(db, user) -> Organization:
    svc = OrgService(db)
    org = await svc.create(
        name=f"O {ULID()}",
        slug=f"o8-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    # Backfilled tenants are TRIAL; activate for purchase tests
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    return org


async def _mk_pack(db, org, user, visibility=PackVisibility.PUBLIC) -> SkillPack:
    pack = SkillPack(
        owner_org_id=org.id,
        name=f"Pack {ULID()}",
        slug=f"pk-{str(ULID()).lower()}",
        status=PackStatus.PUBLISHED,
        visibility=visibility,
        created_by=user.id,
    )
    db.add(pack)
    await db.flush()
    return pack


def _actor(user):
    return Actor(user_id=user.id, type="tenant")


async def _mk_listing(db, seller_org, user, **kw) -> MarketplaceListing:
    pack = await _mk_pack(db, seller_org, user)
    defaults = dict(
        seller_org_id=seller_org.id,
        product_type="skill_pack",
        product_id=pack.id,
        offer_type="paid",
        price_minor=21494,
        currency="USD",
        license_scope="organization",
        seat_limit=None,
        upgrade_policy="all_versions",
        included_plan_keys=[],
        bill_via_invoice=False,
        actor=_actor(user),
    )
    defaults.update(kw)
    listing = await market_svc.create_listing(db, **defaults)
    listing.status = "active"
    await db.flush()
    return listing


# ── Pure economics ───────────────────────────────────────────


def test_split_economics():
    fee, seller, partner = market_svc.split_economics(21494, Decimal("30.00"), Decimal("6"))
    assert fee == 6448  # 30% rounded
    assert seller == 21494 - 6448
    assert partner == 1290  # 6% of gross, comes out of the fee
    # Partner share never exceeds the fee
    fee2, _, partner2 = market_svc.split_economics(1000, Decimal("5"), Decimal("50"))
    assert partner2 == fee2 == 50


# ── Purchase flow ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_purchase_credit_flow_and_grant(db):
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    await credit_svc.top_up(db, buyer_tenant.id, "USD", 50000, actor=_actor(buyer_user))
    purchase = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="credit",
        idempotency_key=f"buy-{ULID()}",
    )
    assert purchase.status == "pending"
    assert purchase.amount_minor == 21494
    snapshot = purchase.economics_snapshot
    assert snapshot["platform_fee_minor"] == 6448
    assert snapshot["seller_org_id"] == seller_org.id
    await credit_svc.debit(
        db,
        buyer_tenant.id,
        "USD",
        purchase.amount_minor,
        reference_type="purchase",
        reference_id=purchase.id,
        idempotency_key=f"purchase:{purchase.id}",
    )
    purchase = await market_svc.mark_purchase_paid(
        db, purchase_id=purchase.id, payment_ref=None, actor=_actor(buyer_user)
    )
    assert purchase.status == "paid"
    grant = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == purchase.id))
    ).scalar_one()
    assert grant.tenant_id == buyer_tenant.id  # from the purchase row, not params
    assert grant.org_id == buyer_org.id
    assert grant.status == "active"
    # Idempotent webhook replay
    again = await market_svc.mark_purchase_paid(
        db, purchase_id=purchase.id, payment_ref="dup", actor=_actor(buyer_user)
    )
    assert again.status == "paid"
    grants = (
        await db.execute(
            select(func.count(LicenseGrant.id)).where(LicenseGrant.purchase_id == purchase.id)
        )
    ).scalar_one()
    assert grants == 1


@pytest.mark.asyncio
async def test_purchase_guards(db):
    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    # Own-tenant purchase rejected
    with pytest.raises(AppError) as exc:
        await market_svc.create_purchase(
            db,
            listing_id=listing.id,
            buyer_org_id=seller_org.id,
            purchaser=_actor(seller_user),
            payment_method="credit",
            idempotency_key=None,
        )
    assert exc.value.code == "ALREADY_OWNED"
    # Duplicate purchase (already licensed) rejected
    buyer_user = await _mk_user(db)
    buyer_org = await _mk_org(db, buyer_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    db.add(
        LicenseGrant(
            listing_id=listing.id,
            product_type="skill_pack",
            product_id=listing.product_id,
            tenant_id=buyer_tenant.id,
            org_id=buyer_org.id,
            scope="organization",
            source="manual_grant",
        )
    )
    await db.flush()
    with pytest.raises(AppError) as exc2:
        await market_svc.create_purchase(
            db,
            listing_id=listing.id,
            buyer_org_id=buyer_org.id,
            purchaser=_actor(buyer_user),
            payment_method="credit",
            idempotency_key=None,
        )
    assert exc2.value.code == "ALREADY_LICENSED"


# ── Install gate matrix ──────────────────────────────────────


@pytest.mark.asyncio
async def test_install_gate_matrix(db):
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)

    # 1. No listing → pass (free semantics preserved for existing installs)
    unlisted_pack = await _mk_pack(db, seller_org, seller_user)
    await market_svc.check_install_license(db, "skill_pack", unlisted_pack.id, buyer_org)

    # 2. paid without grant → LICENSE_REQUIRED
    paid = await _mk_listing(db, seller_org, seller_user)
    with pytest.raises(AppError) as exc:
        await market_svc.check_install_license(db, "skill_pack", paid.product_id, buyer_org)
    assert exc.value.code == "LICENSE_REQUIRED"

    # 3. Seller org installs its own paid product → pass
    await market_svc.check_install_license(db, "skill_pack", paid.product_id, seller_org)

    # 4. paid WITH grant → pass
    db.add(
        LicenseGrant(
            listing_id=paid.id,
            product_type="skill_pack",
            product_id=paid.product_id,
            tenant_id=buyer_tenant.id,
            org_id=buyer_org.id,
            scope="organization",
            source="manual_grant",
        )
    )
    await db.flush()
    await market_svc.check_install_license(db, "skill_pack", paid.product_id, buyer_org)

    # 5. private → uniform 404 for non-seller
    private = await _mk_listing(
        db, seller_org, seller_user, offer_type="private", price_minor=None, currency=None
    )
    with pytest.raises(AppError) as exc2:
        await market_svc.check_install_license(db, "skill_pack", private.product_id, buyer_org)
    assert exc2.value.code == "PACK_NOT_FOUND" and exc2.value.status_code == 404

    # 6. included_with_plan: buyer on community → denied; school key incl. via trial
    included = await _mk_listing(
        db,
        seller_org,
        seller_user,
        offer_type="included_with_plan",
        price_minor=None,
        currency=None,
        included_plan_keys=["school", "growth"],
    )
    with pytest.raises(AppError) as exc3:  # ACTIVE tenant, no sub → community
        await market_svc.check_install_license(db, "skill_pack", included.product_id, buyer_org)
    assert exc3.value.code == "LICENSE_REQUIRED"
    # Flip the buyer to TRIAL (school entitlements) → pass + lazy grant
    from datetime import timedelta

    buyer_tenant.status = TenantStatus.TRIAL
    buyer_tenant.trial_ends_at = datetime.now(UTC) + timedelta(days=7)
    await db.flush()
    from app.controlplane.services.entitlements import invalidate_cache

    await invalidate_cache(buyer_tenant.id)
    await market_svc.check_install_license(db, "skill_pack", included.product_id, buyer_org)
    lazy = (
        await db.execute(
            select(LicenseGrant).where(
                LicenseGrant.product_id == included.product_id,
                LicenseGrant.tenant_id == buyer_tenant.id,
                LicenseGrant.source == "plan_included",
            )
        )
    ).scalar_one()
    assert lazy.status == "active"

    # 7. partner_only without attribution → not purchasable
    partner_only = await _mk_listing(db, seller_org, seller_user, offer_type="partner_only")
    with pytest.raises(AppError) as exc4:
        await market_svc.create_purchase(
            db,
            listing_id=partner_only.id,
            buyer_org_id=buyer_org.id,
            purchaser=_actor(buyer_user),
            payment_method="credit",
            idempotency_key=None,
        )
    assert exc4.value.code == "LISTING_NOT_PURCHASABLE"


@pytest.mark.asyncio
async def test_refund_revokes_license_but_preserves_content(db):
    """Issue §27 acceptance: refund blocks NEW installs; nothing is deleted."""
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    listing = await _mk_listing(db, seller_org, seller_user)
    await credit_svc.top_up(db, buyer_tenant.id, "USD", 50000, actor=_actor(buyer_user))
    purchase = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="credit",
        idempotency_key=None,
    )
    await credit_svc.debit(
        db,
        buyer_tenant.id,
        "USD",
        purchase.amount_minor,
        reference_type="purchase",
        reference_id=purchase.id,
        idempotency_key=f"purchase:{purchase.id}",
    )
    purchase = await market_svc.mark_purchase_paid(
        db, purchase_id=purchase.id, payment_ref=None, actor=_actor(buyer_user)
    )
    # Simulate installed content (a row that must survive)
    from app.models.skill_pack import InstallStatus, SkillPackInstallation

    install = SkillPackInstallation(
        org_id=buyer_org.id,
        pack_id=listing.product_id,
        installed_version="1.0.0",
        status=InstallStatus.ACTIVE,
        installed_by=buyer_user.id,
    )
    db.add(install)
    await db.flush()
    balance_before = (
        await db.execute(
            select(credit_svc.TenantCreditBalance.balance_minor).where(
                credit_svc.TenantCreditBalance.tenant_id == buyer_tenant.id
            )
        )
    ).scalar_one()
    refunded = await market_svc.refund_purchase(
        db, purchase.id, reason="client cancelled project", actor=_actor(buyer_user)
    )
    assert refunded.status == "refunded"
    grant = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == purchase.id))
    ).scalar_one()
    assert grant.status == "revoked"
    # Credit refunded
    balance_after = (
        await db.execute(
            select(credit_svc.TenantCreditBalance.balance_minor).where(
                credit_svc.TenantCreditBalance.tenant_id == buyer_tenant.id
            )
        )
    ).scalar_one()
    assert balance_after == balance_before + purchase.amount_minor
    # Installed content untouched
    still_there = await db.get(SkillPackInstallation, install.id)
    assert still_there is not None and still_there.status == InstallStatus.ACTIVE
    # New install now blocked
    with pytest.raises(AppError) as exc:
        await market_svc.check_install_license(db, "skill_pack", listing.product_id, buyer_org)
    assert exc.value.code == "LICENSE_REQUIRED"
    # Double refund rejected
    with pytest.raises(AppError):
        await market_svc.refund_purchase(db, purchase.id, reason="again", actor=_actor(buyer_user))


@pytest.mark.asyncio
async def test_commission_snapshot_isolation(db):
    """Issue §28 acceptance: commission changes affect NEW purchases only."""
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user, price_minor=10000)
    purchase1 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="credit",
        idempotency_key=f"c1-{ULID()}",
    )
    assert purchase1.platform_fee_minor == 3000  # 30%
    frozen = dict(purchase1.economics_snapshot)
    # Platform changes the commission afterwards
    listing.platform_commission_pct = Decimal("50.00")
    await db.flush()
    await db.refresh(purchase1)
    assert dict(purchase1.economics_snapshot) == frozen  # untouched
    # A second buyer purchases at the NEW rate
    buyer2 = await _mk_user(db)
    org2 = await _mk_org(db, buyer2)
    purchase2 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=org2.id,
        purchaser=_actor(buyer2),
        payment_method="credit",
        idempotency_key=f"c2-{ULID()}",
    )
    assert purchase2.platform_fee_minor == 5000  # 50%


@pytest.mark.asyncio
async def test_purchase_accrues_seller_share_via_outbox():
    from app.controlplane.models.partner import RevenueShareEntry
    from app.controlplane.worker import process_outbox_once
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as db:
            seller_user = await _mk_user(db)
            buyer_user = await _mk_user(db)
            seller_org = await _mk_org(db, seller_user)
            buyer_org = await _mk_org(db, buyer_user)
            buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
            listing = await _mk_listing(db, seller_org, seller_user, price_minor=10000)
            await credit_svc.top_up(db, buyer_tenant.id, "USD", 50000, actor=_actor(buyer_user))
            purchase = await market_svc.create_purchase(
                db,
                listing_id=listing.id,
                buyer_org_id=buyer_org.id,
                purchaser=_actor(buyer_user),
                payment_method="credit",
                idempotency_key=None,
            )
            await credit_svc.debit(
                db,
                buyer_tenant.id,
                "USD",
                purchase.amount_minor,
                reference_type="purchase",
                reference_id=purchase.id,
                idempotency_key=f"purchase:{purchase.id}",
            )
            await market_svc.mark_purchase_paid(
                db, purchase_id=purchase.id, payment_ref=None, actor=_actor(buyer_user)
            )
            await db.commit()
            purchase_id, seller_org_id = purchase.id, seller_org.id
        # Drain until quiet, SCOPED to this test's topic — unrelated
        # full-suite backlog would otherwise exhaust the pass budget.
        for _ in range(30):
            async with AsyncSessionLocal() as db:
                if await process_outbox_once(db, topics=["purchase.paid"]) == 0:
                    break
        async with AsyncSessionLocal() as db:
            entry = (
                await db.execute(
                    select(RevenueShareEntry).where(
                        RevenueShareEntry.source_id == purchase_id,
                        RevenueShareEntry.beneficiary_org_id == seller_org_id,
                    )
                )
            ).scalar_one_or_none()
            assert entry is not None
            assert entry.share_amount_minor == 7000  # 10000 − 30% fee
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_registry_listings_hides_private_and_draft(db):
    """R25: the PUBLIC batch price-badge endpoint returns only public-offer
    active listings — private/partner-only/draft never surface, and no
    seller-internal fields (commission, seller_tenant_id) leak."""
    from app.controlplane.api.marketplace import registry_listings

    user = await _mk_user(db)
    seller_org = await _mk_org(db, user)
    paid = await _mk_listing(db, seller_org, user, offer_type="paid")
    private = await _mk_listing(
        db, seller_org, user, offer_type="private", price_minor=None, currency=None
    )
    partner_only = await _mk_listing(
        db, seller_org, user, offer_type="partner_only", price_minor=5000, currency="USD"
    )
    draft = await _mk_listing(db, seller_org, user, offer_type="paid")
    draft.status = "draft"
    await db.flush()

    ids = ",".join([paid.product_id, private.product_id, partner_only.product_id, draft.product_id])
    resp = await registry_listings(product_type="skill_pack", product_ids=ids, db=db)
    data = resp.data

    assert paid.product_id in data
    assert private.product_id not in data  # anti-enumeration
    assert partner_only.product_id not in data  # not for anonymous public
    assert draft.product_id not in data  # not active
    # No seller-internal fields in the public payload
    import json as _json

    blob = _json.dumps(data)
    for leak in ("commission_pct", "seller_tenant_id", "bill_via_invoice", "seller_org_id"):
        assert leak not in blob, leak


# ── R44/R72: license-gate + purchase dedup + idempotency scoping ──


@pytest.mark.asyncio
async def test_delisted_listing_keeps_license_gate(db):
    """R44[16]: delisting means 'stop selling', not 'give it away' — the
    install gate must still require a license after delist (else refund
    revocation is nullified by delist+reinstall)."""
    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_user = await _mk_user(db)
    buyer_org = await _mk_org(db, buyer_user)
    # Gate blocks the unlicensed buyer while active.
    with pytest.raises(AppError) as exc:
        await market_svc.check_install_license(db, "skill_pack", listing.product_id, buyer_org)
    assert exc.value.code == "LICENSE_REQUIRED"
    # Delist → the gate must STILL block.
    listing.status = "delisted"
    await db.flush()
    with pytest.raises(AppError) as exc2:
        await market_svc.check_install_license(db, "skill_pack", listing.product_id, buyer_org)
    assert exc2.value.code == "LICENSE_REQUIRED"


@pytest.mark.asyncio
async def test_pending_purchase_dedupes_not_double_charges(db):
    """R44[17]: a second purchase attempt while the first is still pending must
    return the SAME pending purchase, not open a parallel charge."""
    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_user = await _mk_user(db)
    buyer_org = await _mk_org(db, buyer_user)
    p1 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="checkout",
        idempotency_key=None,
    )
    assert p1.status == "pending"
    p2 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="checkout",
        idempotency_key=None,
    )
    assert p2.id == p1.id, "second attempt must resume the pending purchase"


@pytest.mark.asyncio
async def test_purchase_idempotency_scoped_per_tenant(db):
    """R72[2]: the same client idempotency key on two different buyer tenants
    must produce two independent purchases — not return (and charge against)
    the first tenant's row."""
    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer1 = await _mk_user(db)
    org1 = await _mk_org(db, buyer1)
    buyer2 = await _mk_user(db)
    org2 = await _mk_org(db, buyer2)
    key = "checkout-shared-001"
    p1 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=org1.id,
        purchaser=_actor(buyer1),
        payment_method="checkout",
        idempotency_key=key,
    )
    p2 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=org2.id,
        purchaser=_actor(buyer2),
        payment_method="checkout",
        idempotency_key=key,
    )
    assert p1.id != p2.id
    assert p1.buyer_tenant_id != p2.buyer_tenant_id


@pytest.mark.asyncio
async def test_major_locked_blocks_fresh_install_of_newer_major(db):
    """R44[18]: a major_locked license purchased at major 1 must block a FRESH
    install of major 2 (uninstall→reinstall bypass), not just /upgrade."""
    from app.controlplane.models.marketplace import LicenseGrant

    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    listing = await _mk_listing(db, seller_org, seller_user, upgrade_policy="major_locked")
    buyer_user = await _mk_user(db)
    buyer_org = await _mk_org(db, buyer_user)
    db.add(
        LicenseGrant(
            listing_id=listing.id,
            product_type="skill_pack",
            product_id=listing.product_id,
            tenant_id=buyer_org.tenant_id,
            org_id=buyer_org.id,
            scope="organization",
            source="purchase",
            purchased_major=1,
        )
    )
    await db.flush()
    # Same-major install passes.
    await market_svc.check_install_license(
        db, "skill_pack", listing.product_id, buyer_org, target_version="1.4.0"
    )
    # Newer-major FRESH install blocked.
    with pytest.raises(AppError) as exc:
        await market_svc.check_install_license(
            db, "skill_pack", listing.product_id, buyer_org, target_version="2.0.0"
        )
    assert exc.value.code == "LICENSE_UPGRADE_REQUIRED"


@pytest.mark.asyncio
async def test_manual_seat_limited_grant_requires_limit(db):
    """R44[20]: a seat_limited manual grant without a positive seat_limit must
    be rejected — NULL silently disabled the seat check."""
    user = await _mk_user(db)
    org = await _mk_org(db, user)
    with pytest.raises(AppError) as exc:
        await market_svc.manual_grant(
            db,
            product_type="skill_pack",
            product_id=str(ULID()),
            tenant_id=org.tenant_id,
            scope="seat_limited",
            org_id=org.id,
            expires_at=None,
            actor=_actor(user),
        )
    assert exc.value.code == "LISTING_INVALID"
    # With a limit it succeeds and stores it.
    grant = await market_svc.manual_grant(
        db,
        product_type="skill_pack",
        product_id=str(ULID()),
        tenant_id=org.tenant_id,
        scope="seat_limited",
        org_id=org.id,
        expires_at=None,
        actor=_actor(user),
        seat_limit=25,
    )
    assert grant.seat_limit == 25


@pytest.mark.asyncio
async def test_invoice_billed_purchase_delivers_and_queues_line(db):
    """R44[22]: payment_method='invoice' (bill_via_invoice listings only)
    delivers the license immediately; the charge is picked up as a license
    line at period close (payment_method='invoice', invoice_id NULL)."""
    from app.controlplane.models.marketplace import LicenseGrant

    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    inv_listing = await _mk_listing(db, seller_org, seller_user, bill_via_invoice=True)
    cash_listing = await _mk_listing(db, seller_org, seller_user)  # bill_via_invoice=False
    buyer_user = await _mk_user(db)
    buyer_org = await _mk_org(db, buyer_user)
    # invoice billing rejected for a non-flagged listing
    with pytest.raises(AppError) as exc:
        await market_svc.create_purchase(
            db,
            listing_id=cash_listing.id,
            buyer_org_id=buyer_org.id,
            purchaser=_actor(buyer_user),
            payment_method="invoice",
            idempotency_key=None,
        )
    assert exc.value.code == "LISTING_NOT_PURCHASABLE"
    # flagged listing: purchase → mark paid → grant exists, invoice_id NULL
    p = await market_svc.create_purchase(
        db,
        listing_id=inv_listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="invoice",
        idempotency_key=None,
    )
    paid = await market_svc.mark_purchase_paid(
        db, purchase_id=p.id, payment_ref=None, actor=_actor(buyer_user)
    )
    assert paid.status == "paid" and paid.payment_method == "invoice"
    assert paid.invoice_id is None  # awaits the period close license line
    grant = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == p.id))
    ).scalar_one()
    assert grant.status == "active"


@pytest.mark.asyncio
async def test_learning_path_install_consumes_license(db):
    """R49[36]: learning_path is purchasable but nothing consumed the license —
    buyers paid and had no way to obtain the content. install_from_listing is
    the §8.5 mechanism: license-gated cross-org fork of the path + items."""
    from app.models.learning_path import LearningPath, LearningPathItem, PathItemType
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="Video Mastery")
    path.status = ContentStatus.PUBLISHED
    await db.flush()
    await lp_svc.add_item(path.id, seller_org.id, "section", section_title="Week 1", sort_order=0)

    listing = await market_svc.create_listing(
        db,
        seller_org_id=seller_org.id,
        product_type="learning_path",
        product_id=path.id,
        offer_type="paid",
        price_minor=9900,
        currency="USD",
        license_scope="organization",
        seat_limit=None,
        upgrade_policy="all_versions",
        included_plan_keys=[],
        bill_via_invoice=False,
        actor=_actor(seller_user),
    )
    listing.status = "active"
    await db.flush()

    # Unlicensed buyer → LICENSE_REQUIRED, nothing copied
    with pytest.raises(AppError) as exc:
        await lp_svc.install_from_listing(buyer_org.id, listing.id, buyer_user.id)
    assert exc.value.code == "LICENSE_REQUIRED"

    # Grant a license (manual grant = the paid path's outcome)
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    copy = await lp_svc.install_from_listing(buyer_org.id, listing.id, buyer_user.id)
    assert copy.org_id == buyer_org.id
    assert copy.id != path.id
    assert copy.name == "Video Mastery"
    items = (
        (await db.execute(select(LearningPathItem).where(LearningPathItem.path_id == copy.id)))
        .scalars()
        .all()
    )
    assert len(items) == 1 and items[0].item_type == PathItemType.SECTION
    # Source path untouched
    src = await db.get(LearningPath, path.id)
    assert src.org_id == seller_org.id


@pytest.mark.asyncio
async def test_learning_path_install_blocks_missing_workflow_deps(db):
    """R49[36]: items referencing workflow packs the buyer hasn't installed →
    hard 422 listing the gaps, nothing copied."""
    from app.models.learning_path import LearningPath
    from app.models.skill import ContentStatus
    from app.models.skill_pack import InstallStatus
    from app.models.workflow_pack import WorkflowPack, WorkflowPackInstallation
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    wf_pack = WorkflowPack(
        owner_org_id=seller_org.id,
        name=f"WF {ULID()}",
        slug=f"wf-{str(ULID()).lower()}",
        visibility=PackVisibility.PUBLIC,
        created_by=seller_user.id,
    )
    db.add(wf_pack)
    await db.flush()
    # Seller org has it "installed" so add_item passes
    db.add(
        WorkflowPackInstallation(
            org_id=seller_org.id,
            pack_id=wf_pack.id,
            installed_version="1.0.0",
            status=InstallStatus.ACTIVE,
            installed_by=seller_user.id,
        )
    )
    await db.flush()

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="WF Path")
    path.status = ContentStatus.PUBLISHED
    await db.flush()
    await lp_svc.add_item(
        path.id, seller_org.id, "workflow_pack", workflow_pack_id=wf_pack.id, sort_order=0
    )

    listing = await market_svc.create_listing(
        db,
        seller_org_id=seller_org.id,
        product_type="learning_path",
        product_id=path.id,
        offer_type="paid",
        price_minor=5000,
        currency="USD",
        license_scope="organization",
        seat_limit=None,
        upgrade_policy="all_versions",
        included_plan_keys=[],
        bill_via_invoice=False,
        actor=_actor(seller_user),
    )
    listing.status = "active"
    await db.flush()
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )

    with pytest.raises(AppError) as exc:
        await lp_svc.install_from_listing(buyer_org.id, listing.id, buyer_user.id)
    assert exc.value.code == "PATH_DEPENDENCY_MISSING"
    assert wf_pack.id in exc.value.message
    # nothing copied
    count = (
        await db.execute(
            select(func.count(LearningPath.id)).where(LearningPath.org_id == buyer_org.id)
        )
    ).scalar_one()
    assert count == 0

    # Buyer installs the dependency → copy succeeds with the wf item intact
    db.add(
        WorkflowPackInstallation(
            org_id=buyer_org.id,
            pack_id=wf_pack.id,
            installed_version="1.0.0",
            status=InstallStatus.ACTIVE,
            installed_by=buyer_user.id,
        )
    )
    await db.flush()
    copy = await lp_svc.install_from_listing(buyer_org.id, listing.id, buyer_user.id)
    assert copy.org_id == buyer_org.id


# ── R86/R87/R88: registry re-check, resubmit version, seller currency ──


@pytest.mark.asyncio
async def test_registry_badge_rechecks_product_liveness(db):
    """R86[7]: the public badge endpoint filtered only listing columns —
    archived/private products and deleted seller orgs kept leaking
    existence + price + seller name. The endpoint re-checks the product."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.main import app
    from app.models.skill_pack import PackStatus, PackVisibility

    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    pack_id = listing.product_id
    await db.commit()

    @asynccontextmanager
    async def _noop(a):
        yield

    async def badge(pid):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get(
                "/api/v1/registry/listings",
                params={"product_type": "skill_pack", "product_ids": pid},
            )
            assert r.status_code == 200, r.text
            return r.json()["data"]

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        # published+public → badge present
        data = await badge(pack_id)
        assert pack_id in data
        # archive the pack (listing untouched — the old bug's setup)
        pack = await db.get(SkillPack, pack_id)
        pack.status = PackStatus.ARCHIVED
        await db.commit()
        data = await badge(pack_id)
        assert pack_id not in data, "archived product still exposed by public badge"
        # restore, then flip private
        pack.status = PackStatus.PUBLISHED
        pack.visibility = PackVisibility.PRIVATE
        await db.commit()
        data = await badge(pack_id)
        assert pack_id not in data, "private product still exposed by public badge"
    finally:
        app.router.lifespan_context = orig
        # restore for other tests
        pack = await db.get(SkillPack, pack_id)
        pack.status = PackStatus.PUBLISHED
        pack.visibility = PackVisibility.PUBLIC
        await db.commit()


@pytest.mark.asyncio
async def test_resubmission_bumps_version_and_new_decision_lands(db):
    """R87[8]: submit_draft resubmitted the SAME version after
    REVISION_REQUESTED, so the portal decision-idempotency key never changed
    and the client's decision on the NEW work was swallowed. Resubmit now
    bumps version."""
    from app.models.project import SubmissionStatus
    from app.services.project import ProjectService

    user = await _mk_user(db)
    org = await _mk_org(db, user)
    svc = ProjectService(db)
    proj = await svc.create_project(
        org.id,
        "RSB",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        user.id,
    )
    sub = await svc.create_submission(org.id, proj.id, user.id)
    await svc.submit_draft(sub.id, user.id)
    assert sub.version == 1
    sub.status = SubmissionStatus.REVISION_REQUESTED
    await db.flush()
    await svc.submit_draft(sub.id, user.id)  # resubmit after revision
    assert sub.version == 2, "resubmission must bump the version"


@pytest.mark.asyncio
async def test_seller_accrual_converted_to_platform_currency(db):
    """R88[9] CRITICAL: seller entries were written in BUYER currency while
    seller_org statements hardcode the platform currency and sum
    unconverted — a KRW share settled as the same number of USD cents.
    Seller accrual now converts at purchase time (FX snapshotted)."""
    from datetime import UTC as _UTC
    from datetime import datetime as _dt

    from app.controlplane.models.marketplace import MarketplacePurchase
    from app.controlplane.models.partner import RevenueShareEntry
    from app.controlplane.services import pricing as pricing_svc
    from app.controlplane.services import revenue_share as revshare_svc

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    # KRW buyer tenant
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    buyer_tenant.currency = "KRW"
    await db.flush()
    listing = await _mk_listing(db, seller_org, seller_user, price_minor=1_300_000, currency="KRW")
    # FX: KRW -> USD
    from datetime import timedelta as _tdel

    await pricing_svc.create_fx_rate(
        db,
        actor=_actor(seller_user),
        base_currency="KRW",
        quote_currency="USD",
        rate=Decimal("0.00077"),
        effective_from=_dt.now(_UTC) - _tdel(days=1),
    )
    purchase = MarketplacePurchase(
        listing_id=listing.id,
        buyer_tenant_id=buyer_tenant.id,
        buyer_org_id=buyer_org.id,
        purchaser_user_id=buyer_user.id,
        status="paid",
        amount_minor=1_300_000,
        currency="KRW",
        seller_share_minor=1_040_000,
        platform_fee_minor=260_000,
        economics_snapshot={"seller_org_id": seller_org.id},
        payment_method="credit",
    )
    db.add(purchase)
    await db.flush()
    created = await revshare_svc.accrue_for_purchase(db, purchase.id)
    assert created == 1
    entry = (
        await db.execute(
            select(RevenueShareEntry).where(
                RevenueShareEntry.source_id == purchase.id,
                RevenueShareEntry.beneficiary_type == "seller_org",
            )
        )
    ).scalar_one()
    assert entry.currency == "USD", "seller entry must be in the settlement currency"
    # ₩1,040,000 (KRW minor mult 1) × 0.00077 = $800.80 → 80080 USD minor
    assert entry.share_amount_minor == 80080, entry.share_amount_minor
    assert entry.fx_rate_snapshot is not None


# ── R129 batch regressions ───────────────────────────────────


@pytest.mark.asyncio
async def test_listingless_install_requires_active_grant(db):
    """R129[C0]: a product_id with NO listing must NOT free-pass — any org
    could copy any tenant's published learning path (cross-tenant content
    theft). The listing-less path is legitimate only under a manual grant."""
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    thief_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    thief_org = await _mk_org(db, thief_user)

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="Unlisted Gold")
    path.status = ContentStatus.PUBLISHED
    await db.flush()

    # No listing, no grant → uniform 404 (never LICENSE_REQUIRED — that
    # would confirm the path exists).
    with pytest.raises(AppError) as exc:
        await lp_svc.install_from_listing(thief_org.id, None, thief_user.id, product_id=path.id)
    assert exc.value.code == "LISTING_NOT_FOUND"

    # With an active manual grant the same call succeeds.
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=thief_org.tenant_id,
        scope="organization",
        org_id=thief_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    copy = await lp_svc.install_from_listing(thief_org.id, None, thief_user.id, product_id=path.id)
    assert copy.org_id == thief_org.id
    assert copy.origin_source_path_id == path.id


@pytest.mark.asyncio
async def test_listingless_install_dedupe_not_by_name(db):
    """R129[M2]: listing-less dedupe keys on origin_source_path_id — an org's
    own locally-authored path with the SAME NAME must not be returned as the
    'installed copy', and a retry must return the true copy, not mint another."""
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    src = await lp_svc.create_path(seller_org.id, seller_user.id, name="Same Name")
    src.status = ContentStatus.PUBLISHED
    # Buyer already has a LOCAL path with the identical name.
    local = await lp_svc.create_path(buyer_org.id, buyer_user.id, name="Same Name")
    await db.flush()

    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=src.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    copy = await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=src.id)
    assert copy.id != local.id, "dedupe must not match the org's local same-named path"
    assert copy.origin_source_path_id == src.id
    # Retry returns the SAME copy (idempotent), still not the local one.
    again = await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=src.id)
    assert again.id == copy.id


@pytest.mark.asyncio
async def test_draft_listing_does_not_strand_manual_grant(db):
    """R129[M3]: a DRAFT listing on the product must not capture the
    product_id resolve and 404 a legit manual-grant redemption."""
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="Draft Listed")
    path.status = ContentStatus.PUBLISHED
    await db.flush()
    # A draft listing exists (seller preparing a sale) but is not active.
    await market_svc.create_listing(
        db,
        seller_org_id=seller_org.id,
        product_type="learning_path",
        product_id=path.id,
        offer_type="paid",
        price_minor=9900,
        currency="USD",
        license_scope="organization",
        seat_limit=None,
        upgrade_policy="all_versions",
        included_plan_keys=[],
        bill_via_invoice=False,
        actor=_actor(seller_user),
    )
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    copy = await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=path.id)
    assert copy.org_id == buyer_org.id


@pytest.mark.asyncio
async def test_mark_paid_skips_grant_when_already_licensed(db):
    """R129[H0]: a stale checkout completing AFTER the tenant already holds an
    active grant (e.g. from an earlier purchase) must not mint a second
    grant for the same product."""
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    await credit_svc.top_up(db, buyer_tenant.id, "USD", 100000, actor=_actor(buyer_user))

    # Two pending purchases: DIFFERENT payment methods so the R123[H8]
    # same-method pending-resume doesn't collapse them (checkout tab left
    # stale while the buyer completes via credit — the exact H0 shape).
    p1 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="credit",
        idempotency_key=f"h0a-{ULID()}",
    )
    p2 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="checkout",
        idempotency_key=f"h0b-{ULID()}",
    )
    await market_svc.mark_purchase_paid(
        db, purchase_id=p1.id, payment_ref="sess1", actor=_actor(buyer_user)
    )
    await market_svc.mark_purchase_paid(
        db, purchase_id=p2.id, payment_ref="sess2", actor=_actor(buyer_user)
    )
    grants = (
        await db.execute(
            select(func.count(LicenseGrant.id)).where(
                LicenseGrant.tenant_id == buyer_tenant.id,
                LicenseGrant.product_id == listing.product_id,
                LicenseGrant.status == "active",
            )
        )
    ).scalar_one()
    assert grants == 1, "duplicate checkout completion must not mint a second grant"


# ── R130 grant-semantics regressions ─────────────────────────


@pytest.mark.asyncio
async def test_listingless_gate_full_grant_semantics(db):
    """R130[7]/[8]/[11]: the listing-less gate must apply the SAME semantics
    as _find_covering_grant — expired grants don't redeem, org-scoped grants
    don't cover sibling orgs — and a tenant's OWN unlisted path installs
    into a sibling org without any grant."""
    from datetime import timedelta

    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="Sem Path")
    path.status = ContentStatus.PUBLISHED
    await db.flush()

    # (a) EXPIRED grant → still 404 (expiry is read-time; status stays active)
    expired = await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        actor=_actor(seller_user),
    )
    assert expired.status == "active"  # never swept
    with pytest.raises(AppError) as exc:
        await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=path.id)
    assert exc.value.code == "LISTING_NOT_FOUND"

    # (b) grant org-scoped to ANOTHER org of the same tenant → 404 here
    other_user = await _mk_user(db)
    svc = OrgService(db)
    sibling = await svc.create(
        name=f"Sib {ULID()}",
        slug=f"sib-{str(ULID()).lower()}",
        description=None,
        created_by=other_user.id,
    )
    sibling.tenant_id = buyer_org.tenant_id  # same tenant, different org
    await db.flush()
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=sibling.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    with pytest.raises(AppError) as exc2:
        await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=path.id)
    assert exc2.value.code == "LISTING_NOT_FOUND"

    # (c) own-tenant bypass: an org of the SELLER's tenant installs the
    # tenant's own unlisted path with no grant at all.
    seller_sibling = await svc.create(
        name=f"SSib {ULID()}",
        slug=f"ssib-{str(ULID()).lower()}",
        description=None,
        created_by=seller_user.id,
    )
    seller_sibling.tenant_id = seller_org.tenant_id
    await db.flush()
    copy = await lp_svc.install_from_listing(
        seller_sibling.id, None, seller_user.id, product_id=path.id
    )
    assert copy.org_id == seller_sibling.id


@pytest.mark.asyncio
async def test_mark_paid_covering_semantics_and_expiry(db):
    """R130[6]/[9]/[31]: the duplicate-grant guard uses covering semantics —
    an EXPIRED grant must NOT suppress a paid renewal's mint, and a
    tenant-wide grant MUST suppress an org-scoped duplicate."""
    from datetime import timedelta

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)

    # (a) expired grant → renewal purchase MUST mint a fresh grant
    await market_svc.manual_grant(
        db,
        product_type=listing.product_type,
        product_id=listing.product_id,
        tenant_id=buyer_tenant.id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        actor=_actor(seller_user),
    )
    p1 = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="checkout",
        idempotency_key=f"renew-{ULID()}",
    )
    await market_svc.mark_purchase_paid(
        db, purchase_id=p1.id, payment_ref="renew1", actor=_actor(buyer_user)
    )
    fresh = (
        await db.execute(
            select(func.count(LicenseGrant.id)).where(
                LicenseGrant.purchase_id == p1.id, LicenseGrant.status == "active"
            )
        )
    ).scalar_one()
    assert fresh == 1, "expired grant must not suppress a paid renewal's grant"

    # (b) tenant-WIDE covering grant suppresses an org-scoped duplicate mint
    seller2 = await _mk_user(db)
    buyer2 = await _mk_user(db)
    s_org2 = await _mk_org(db, seller2)
    b_org2 = await _mk_org(db, buyer2)
    listing2 = await _mk_listing(db, s_org2, seller2)
    t2 = await db.get(TenantAccount, b_org2.tenant_id)
    # H0 shape: the checkout purchase is created FIRST (no coverage yet),
    # the covering tenant-wide grant lands while it is pending (e.g. a
    # manual grant / another channel), THEN the stale checkout completes.
    p2 = await market_svc.create_purchase(
        db,
        listing_id=listing2.id,
        buyer_org_id=b_org2.id,
        purchaser=_actor(buyer2),
        payment_method="checkout",
        idempotency_key=f"dup2-{ULID()}",
    )
    # (c)'s purchase must also predate any covering grant (precheck blocks
    # otherwise); different payment method so H8 pending-resume doesn't merge.
    p3 = await market_svc.create_purchase(
        db,
        listing_id=listing2.id,
        buyer_org_id=b_org2.id,
        purchaser=_actor(buyer2),
        payment_method="credit",
        idempotency_key=f"dup3-{ULID()}",
    )
    await market_svc.manual_grant(
        db,
        product_type=listing2.product_type,
        product_id=listing2.product_id,
        tenant_id=t2.id,
        scope="tenant",
        org_id=None,
        expires_at=None,
        actor=_actor(seller2),
    )
    await market_svc.mark_purchase_paid(
        db, purchase_id=p2.id, payment_ref="dup2", actor=_actor(buyer2)
    )
    minted = (
        await db.execute(
            select(func.count(LicenseGrant.id)).where(LicenseGrant.purchase_id == p2.id)
        )
    ).scalar_one()
    assert minted == 0, "tenant-wide covering grant must suppress the duplicate mint"

    # (c) duplicate active grants must not crash the guard (R130[5])
    for _ in range(2):
        await market_svc.manual_grant(
            db,
            product_type=listing2.product_type,
            product_id=listing2.product_id,
            tenant_id=t2.id,
            scope="organization",
            org_id=b_org2.id,
            expires_at=None,
            actor=_actor(seller2),
        )
    # No MultipleResultsFound — completes cleanly.
    got = await market_svc.mark_purchase_paid(
        db, purchase_id=p3.id, payment_ref=None, actor=_actor(buyer2)
    )
    assert got.status == "paid"


@pytest.mark.asyncio
async def test_grant_install_then_listing_purchase_no_duplicate_copy(db):
    """R130[10]: a manual-grant install followed by a listing-backed install
    of the SAME source must return the existing copy, not mint a second."""
    from app.models.learning_path import LearningPath
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="Dup Path")
    path.status = ContentStatus.PUBLISHED
    await db.flush()
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    copy1 = await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=path.id)

    # Seller then lists the path; the buyer installs via the listing.
    listing = await market_svc.create_listing(
        db,
        seller_org_id=seller_org.id,
        product_type="learning_path",
        product_id=path.id,
        offer_type="paid",
        price_minor=9900,
        currency="USD",
        license_scope="organization",
        seat_limit=None,
        upgrade_policy="all_versions",
        included_plan_keys=[],
        bill_via_invoice=False,
        actor=_actor(seller_user),
    )
    listing.status = "active"
    await db.flush()
    copy2 = await lp_svc.install_from_listing(buyer_org.id, listing.id, buyer_user.id)
    assert copy2.id == copy1.id, "listing install must find the manual-grant copy"
    live = (
        await db.execute(
            select(func.count(LearningPath.id)).where(
                LearningPath.org_id == buyer_org.id,
                LearningPath.origin_source_path_id == path.id,
                LearningPath.status != ContentStatus.ARCHIVED,
            )
        )
    ).scalar_one()
    assert live == 1


# ── R131 regressions ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_own_tenant_bypass_rejects_purchased_copies(db):
    """R131 CRITICAL: the own-tenant bypass must qualify only AUTHORED paths —
    an installed COPY of another tenant's paid content (origin markers set)
    must not be re-fanned to sibling orgs via the bypass (license laundering,
    survives refund revocation)."""
    from app.models.learning_path import LearningPath
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    src = await lp_svc.create_path(seller_org.id, seller_user.id, name="Paid Gold")
    src.status = ContentStatus.PUBLISHED
    await db.flush()
    # Buyer legitimately licensed + installed a copy (org-scoped grant).
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=src.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    copy = await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=src.id)
    copy.status = ContentStatus.PUBLISHED  # buyer publishes the copy locally
    await db.flush()

    # Buyer's SIBLING org (same tenant, no grant) tries to install the COPY
    # by its product_id — the bypass must NOT treat the copy as "own".
    sibling_user = await _mk_user(db)
    svc = OrgService(db)
    sibling = await svc.create(
        name=f"LSib {ULID()}",
        slug=f"lsib-{str(ULID()).lower()}",
        description=None,
        created_by=sibling_user.id,
    )
    sibling.tenant_id = buyer_org.tenant_id
    await db.flush()
    with pytest.raises(AppError) as exc:
        await lp_svc.install_from_listing(sibling.id, None, sibling_user.id, product_id=copy.id)
    assert exc.value.code == "LISTING_NOT_FOUND"
    # And no second copy exists anywhere in the tenant.
    copies = (
        await db.execute(
            select(func.count(LearningPath.id)).where(
                LearningPath.org_id == sibling.id,
            )
        )
    ).scalar_one()
    assert copies == 0


@pytest.mark.asyncio
async def test_listingless_seat_limit_enforced(db):
    """R131 ([4]): seat_limited occupancy binds on the listing-less path."""
    from app.models.organization import MemberStatus, OrgMember, OrgRole
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="Seat Path")
    path.status = ContentStatus.PUBLISHED
    await db.flush()
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=buyer_org.tenant_id,
        scope="seat_limited",
        org_id=buyer_org.id,
        seat_limit=1,
        expires_at=None,
        actor=_actor(seller_user),
    )
    # Two active students → occupancy 2 > limit 1.
    for _ in range(2):
        student = await _mk_user(db)
        db.add(
            OrgMember(
                org_id=buyer_org.id,
                user_id=student.id,
                role=OrgRole.STUDENT,
                status=MemberStatus.ACTIVE,
            )
        )
    await db.flush()
    with pytest.raises(AppError) as exc:
        await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=path.id)
    assert exc.value.code == "SEAT_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_tenant_scope_purchase_not_suppressed_by_narrower_grant(db):
    """R131 ([3]): a tenant-scope purchase must mint even when an ORG-scoped
    grant covers the buyer org — the tenant paid for the WIDER scope."""
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user, license_scope="tenant")
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)

    # Pending checkout purchase created BEFORE the narrow grant lands.
    p = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="checkout",
        idempotency_key=f"narrow-{ULID()}",
    )
    await market_svc.manual_grant(
        db,
        product_type=listing.product_type,
        product_id=listing.product_id,
        tenant_id=buyer_tenant.id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    await market_svc.mark_purchase_paid(
        db, purchase_id=p.id, payment_ref="narrow", actor=_actor(buyer_user)
    )
    minted = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == p.id))
    ).scalar_one_or_none()
    assert minted is not None and minted.scope == "tenant", (
        "narrower org grant must not suppress the paid tenant-wide mint"
    )


# ── R132 grant-width regressions ─────────────────────────────


def test_grant_covers_listing_width_matrix():
    """R132 ([F0]/[F1]/[F2]): pure width matrix — scope, duration, seats."""
    from types import SimpleNamespace

    from app.controlplane.services.marketplace import grant_covers_listing_width

    def g(scope, expires_at=None, seat_limit=None, purchased_major=None):
        return SimpleNamespace(
            scope=scope,
            expires_at=expires_at,
            seat_limit=seat_limit,
            purchased_major=purchased_major,
        )

    def li(scope, seat_limit=None, upgrade_policy="all_versions"):
        return SimpleNamespace(
            license_scope=scope, seat_limit=seat_limit, upgrade_policy=upgrade_policy
        )

    from datetime import UTC, datetime

    future = datetime(2099, 1, 1, tzinfo=UTC)
    # scope width
    assert grant_covers_listing_width(g("tenant"), li("tenant"))
    assert not grant_covers_listing_width(g("organization"), li("tenant"))
    assert grant_covers_listing_width(g("tenant"), li("organization"))
    assert grant_covers_listing_width(g("organization"), li("organization"))
    # duration: ANY expiring grant never covers a perpetual purchase
    assert not grant_covers_listing_width(g("tenant", expires_at=future), li("tenant"))
    assert not grant_covers_listing_width(g("organization", expires_at=future), li("organization"))
    # seat capacity
    assert not grant_covers_listing_width(g("seat_limited", seat_limit=5), li("organization"))
    assert not grant_covers_listing_width(
        g("seat_limited", seat_limit=5), li("seat_limited", seat_limit=10)
    )
    assert grant_covers_listing_width(
        g("seat_limited", seat_limit=10), li("seat_limited", seat_limit=5)
    )
    # R135: major axis under major_locked — a paid grant pinned below the
    # current latest major does NOT cover (the upgrade purchase must not 409),
    # while unpinned (manual/plan) grants and all_versions listings do.
    assert not grant_covers_listing_width(
        g("organization", purchased_major=1),
        li("organization", upgrade_policy="major_locked"),
        latest_major=2,
    )
    assert grant_covers_listing_width(
        g("organization", purchased_major=2),
        li("organization", upgrade_policy="major_locked"),
        latest_major=2,
    )
    assert grant_covers_listing_width(
        g("organization", purchased_major=None),
        li("organization", upgrade_policy="major_locked"),
        latest_major=2,
    )
    assert grant_covers_listing_width(
        g("organization", purchased_major=1), li("organization"), latest_major=None
    )


@pytest.mark.asyncio
async def test_org_grant_holder_can_buy_tenant_upgrade(db):
    """R132 ([F0]): an org-scoped grant must not 409 the tenant-scope upgrade
    purchase at the precheck."""
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user, license_scope="tenant")
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    await market_svc.manual_grant(
        db,
        product_type=listing.product_type,
        product_id=listing.product_id,
        tenant_id=buyer_tenant.id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    # Upgrade purchase goes through (no ALREADY_LICENSED).
    p = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="checkout",
        idempotency_key=f"upg-{ULID()}",
    )
    assert p.status == "pending"
    # And completion mints the tenant-wide grant.
    await market_svc.mark_purchase_paid(
        db, purchase_id=p.id, payment_ref="upg", actor=_actor(buyer_user)
    )
    minted = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == p.id))
    ).scalar_one()
    assert minted.scope == "tenant"


@pytest.mark.asyncio
async def test_expiring_trial_grant_does_not_suppress_paid_mint(db):
    """R132 ([F1]): a live-but-expiring trial grant must not suppress the
    perpetual paid mint."""
    from datetime import timedelta

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    # Trial grant: still live, expires in 7 days.
    await market_svc.manual_grant(
        db,
        product_type=listing.product_type,
        product_id=listing.product_id,
        tenant_id=buyer_tenant.id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        actor=_actor(seller_user),
    )
    p = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user),
        payment_method="checkout",
        idempotency_key=f"trial-upg-{ULID()}",
    )
    await market_svc.mark_purchase_paid(
        db, purchase_id=p.id, payment_ref="trialupg", actor=_actor(buyer_user)
    )
    minted = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == p.id))
    ).scalar_one()
    assert minted.expires_at is None, "paid purchase must mint the perpetual grant"


@pytest.mark.asyncio
async def test_manual_grant_copy_not_relistable(db):
    """R132 ([F11]): a manual-grant copy (origin_source_path_id only, no
    listing) of another org's path must not be re-listable for sale."""
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)

    lp_svc = LearningPathService(db)
    src = await lp_svc.create_path(seller_org.id, seller_user.id, name="Grant Copy Src")
    src.status = ContentStatus.PUBLISHED
    await db.flush()
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=src.id,
        tenant_id=buyer_org.tenant_id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    copy = await lp_svc.install_from_listing(buyer_org.id, None, buyer_user.id, product_id=src.id)
    copy.status = ContentStatus.PUBLISHED
    await db.flush()
    # Enable seller feature for the buyer org's tenant (create_listing gate
    # is at the endpoint; the service-level resale gate is what we exercise).
    with pytest.raises(AppError) as exc:
        await market_svc.create_listing(
            db,
            seller_org_id=buyer_org.id,
            product_type="learning_path",
            product_id=copy.id,
            offer_type="paid",
            price_minor=5000,
            currency="USD",
            license_scope="organization",
            seat_limit=None,
            upgrade_policy="all_versions",
            included_plan_keys=[],
            bill_via_invoice=False,
            actor=_actor(buyer_user),
        )
    assert exc.value.code == "LICENSED_CONTENT_NOT_REDISTRIBUTABLE"


@pytest.mark.asyncio
async def test_tenant_wide_seat_limit_caps_tenant_occupancy(db):
    """R132 ([F12]): a tenant-wide (org_id NULL) seat_limited grant caps the
    TENANT's occupancy — not each installing org independently."""
    from app.models.organization import MemberStatus, OrgMember, OrgRole
    from app.models.skill import ContentStatus
    from app.services.learning_path import LearningPathService

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    org_a = await _mk_org(db, buyer_user)
    # Second org in the SAME tenant.
    other_admin = await _mk_user(db)
    svc = OrgService(db)
    org_b = await svc.create(
        name=f"SB {ULID()}",
        slug=f"sb-{str(ULID()).lower()}",
        description=None,
        created_by=other_admin.id,
    )
    org_b.tenant_id = org_a.tenant_id
    await db.flush()

    lp_svc = LearningPathService(db)
    path = await lp_svc.create_path(seller_org.id, seller_user.id, name="TW Seat Path")
    path.status = ContentStatus.PUBLISHED
    await db.flush()
    # Tenant-wide grant capped at 2 seats.
    await market_svc.manual_grant(
        db,
        product_type="learning_path",
        product_id=path.id,
        tenant_id=org_a.tenant_id,
        scope="seat_limited",
        org_id=None,
        seat_limit=2,
        expires_at=None,
        actor=_actor(seller_user),
    )
    # 2 students in org A + 1 in org B → tenant occupancy 3 > 2.
    for org, count in ((org_a, 2), (org_b, 1)):
        for _ in range(count):
            student = await _mk_user(db)
            db.add(
                OrgMember(
                    org_id=org.id,
                    user_id=student.id,
                    role=OrgRole.STUDENT,
                    status=MemberStatus.ACTIVE,
                )
            )
    await db.flush()
    # Installing into org B (1 local student) must still fail: the CAP is
    # tenant-wide and the tenant holds 3 active students.
    with pytest.raises(AppError) as exc:
        await lp_svc.install_from_listing(org_b.id, None, other_admin.id, product_id=path.id)
    assert exc.value.code == "SEAT_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_seat_capacity_upgrade_honored_by_gate(db):
    """R132 ([20]): after a paid seat-capacity upgrade both grants are active;
    the covering-grant resolver must prefer the ROOMIER cap so the upgrade is
    actually honored by the install gate."""
    from app.controlplane.services.marketplace import _find_covering_grant

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    pack = await _mk_pack(db, seller_org, seller_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    for cap in (5, 10):  # old tight grant, then the paid upgrade
        await market_svc.manual_grant(
            db,
            product_type="skill_pack",
            product_id=pack.id,
            tenant_id=buyer_tenant.id,
            scope="seat_limited",
            org_id=buyer_org.id,
            seat_limit=cap,
            expires_at=None,
            actor=_actor(seller_user),
        )
    covering = await _find_covering_grant(db, "skill_pack", pack.id, buyer_tenant.id, buyer_org.id)
    assert covering is not None and covering.seat_limit == 10, (
        "resolver must prefer the roomier (upgraded) seat cap"
    )


@pytest.mark.asyncio
async def test_expiring_wide_trial_does_not_shadow_perpetual_grant(db):
    """R133 ([F10]): the ALREADY_LICENSED precheck must evaluate ALL covering
    grants — an expiring tenant-wide trial (widest by scope, fails duration)
    must not shadow the buyer's perpetual org grant and allow a redundant
    re-purchase of the same org listing."""
    from datetime import timedelta

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user)  # org-scope paid
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    # Perpetual org grant (the earlier purchase).
    await market_svc.manual_grant(
        db,
        product_type=listing.product_type,
        product_id=listing.product_id,
        tenant_id=buyer_tenant.id,
        scope="organization",
        org_id=buyer_org.id,
        expires_at=None,
        actor=_actor(seller_user),
    )
    # Expiring tenant-wide trial (ranks wider by scope).
    await market_svc.manual_grant(
        db,
        product_type=listing.product_type,
        product_id=listing.product_id,
        tenant_id=buyer_tenant.id,
        scope="tenant",
        org_id=None,
        expires_at=datetime.now(UTC) + timedelta(days=14),
        actor=_actor(seller_user),
    )
    with pytest.raises(AppError) as exc:
        await market_svc.create_purchase(
            db,
            listing_id=listing.id,
            buyer_org_id=buyer_org.id,
            purchaser=_actor(buyer_user),
            payment_method="credit",
            idempotency_key=f"shadow-{ULID()}",
        )
    assert exc.value.code == "ALREADY_LICENSED"


@pytest.mark.asyncio
async def test_trial_grant_does_not_unlock_major_bound(db):
    """R133 ([F11]): a purchased_major=NULL trial grant shadowing the paid
    grant must not lift the major_locked bound — the buyer's highest PAID
    major governs."""
    from datetime import timedelta

    from app.controlplane.services.marketplace import check_upgrade_license

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user, upgrade_policy="major_locked")
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    # Paid org grant locked to major 1.
    db.add(
        LicenseGrant(
            listing_id=listing.id,
            product_type=listing.product_type,
            product_id=listing.product_id,
            tenant_id=buyer_tenant.id,
            org_id=buyer_org.id,
            scope="organization",
            source="purchase",
            purchased_major=1,
        )
    )
    # Wider expiring trial with NO purchased_major.
    await market_svc.manual_grant(
        db,
        product_type=listing.product_type,
        product_id=listing.product_id,
        tenant_id=buyer_tenant.id,
        scope="tenant",
        org_id=None,
        expires_at=datetime.now(UTC) + timedelta(days=14),
        actor=_actor(seller_user),
    )
    await db.flush()
    with pytest.raises(AppError) as exc:
        await check_upgrade_license(
            db, listing.product_type, listing.product_id, buyer_org, "2.0.0"
        )
    assert exc.value.code == "LICENSE_UPGRADE_REQUIRED"


@pytest.mark.asyncio
async def test_listing_rejects_seat_limit_on_non_seat_scope(db):
    """R135: a seat_limit on any scope other than seat_limited is dead data —
    enforce_seat_limit only fires on scope == 'seat_limited', so a seller
    pricing a "10-seat team license" on scope=organization silently sold
    unlimited seats. The contradiction must be a 422 at create time (the
    mirror of R44[20], which fixed seat_limited-without-limit)."""
    user = await _mk_user(db)
    org = await _mk_org(db, user)
    with pytest.raises(AppError) as exc:
        await _mk_listing(db, org, user, license_scope="organization", seat_limit=10)
    assert exc.value.code == "LISTING_INVALID"
    with pytest.raises(AppError) as exc2:
        await _mk_listing(db, org, user, license_scope="tenant", seat_limit=5)
    assert exc2.value.code == "LISTING_INVALID"
    # The valid pairing still works.
    listing = await _mk_listing(db, org, user, license_scope="seat_limited", seat_limit=10)
    assert listing.seat_limit == 10


# ── R237: create_listing parameter-validation reject branches ──


@pytest.mark.asyncio
async def test_create_listing_param_validation(db):
    """create_listing's parameter guards (branch-gap): unknown enums, paid-
    needs-price+currency, and the R135 seat_limit↔scope contradictions.
    A weakened guard sells a mispriced/unlimited-seat/dead-scope listing."""
    seller_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    pack = await _mk_pack(db, seller_org, seller_user)
    a = _actor(seller_user)

    def base(**kw):
        d = dict(
            seller_org_id=seller_org.id, product_type="skill_pack", product_id=pack.id,
            offer_type="paid", price_minor=1000, currency="USD",
            license_scope="organization", seat_limit=None, upgrade_policy="all_versions",
            included_plan_keys=[], bill_via_invoice=False, actor=a,
        )
        d.update(kw)
        return d

    async def rejects(**kw):
        with pytest.raises(AppError) as e:
            await market_svc.create_listing(db, **base(**kw))
        assert e.value.code == "LISTING_INVALID"

    await rejects(product_type="quantum_pack")
    await rejects(offer_type="barter")
    await rejects(license_scope="galactic")
    await rejects(offer_type="paid", price_minor=None)         # paid needs price
    await rejects(offer_type="paid", currency=None)            # paid needs currency
    await rejects(license_scope="seat_limited", seat_limit=None)  # seat_limited needs limit
    # R135: seat_limit on a non-seat_limited scope = silently-unlimited seats
    await rejects(license_scope="organization", seat_limit=10)


# ── R264: license revocation + cross-currency purchase arcs ──


@pytest.mark.asyncio
async def test_revoke_grant_arcs(db):
    """R264: revoke_grant was fully untested — unknown grant 404, non-active
    grant 409, and the happy revoke (status/timestamps/reason + audit)."""
    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    await credit_svc.top_up(db, buyer_tenant.id, "USD", 50000, actor=_actor(buyer_user))

    with pytest.raises(AppError) as e:
        await market_svc.revoke_grant(db, str(ULID()), reason="r", actor=_actor(buyer_user))
    assert e.value.code == "LICENSE_NOT_FOUND" and e.value.status_code == 404

    purchase = await market_svc.create_purchase(
        db, listing_id=listing.id, buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user), payment_method="credit",
        idempotency_key=f"rv-{ULID()}")
    await credit_svc.debit(
        db, buyer_tenant.id, "USD", purchase.amount_minor,
        reference_type="purchase", reference_id=purchase.id,
        idempotency_key=f"purchase:{purchase.id}")
    purchase = await market_svc.mark_purchase_paid(
        db, purchase_id=purchase.id, payment_ref=None, actor=_actor(buyer_user))
    grant = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == purchase.id))
    ).scalar_one()

    revoked = await market_svc.revoke_grant(
        db, grant.id, reason="chargeback", actor=_actor(seller_user))
    assert revoked.status == "revoked"
    assert revoked.revoked_at is not None and revoked.revoke_reason == "chargeback"

    with pytest.raises(AppError) as e:                     # second revoke → 409
        await market_svc.revoke_grant(db, grant.id, reason="again", actor=_actor(seller_user))
    assert e.value.code == "PURCHASE_STATUS_CONFLICT" and e.value.status_code == 409


@pytest.mark.asyncio
async def test_purchase_cross_currency_arcs(db):
    """R264: a listing priced in another currency than the buyer tenant —
    missing FX rate → LISTING_NOT_PURCHASABLE 409 (never a silent
    unconverted charge); with a rate the charge converts."""
    from datetime import timedelta

    from app.controlplane.services import pricing as pricing_svc

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user, currency="EUR",
                                price_minor=10000)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    await credit_svc.top_up(db, buyer_tenant.id, "USD", 50000, actor=_actor(buyer_user))

    with pytest.raises(AppError) as e:                     # no EUR→USD rate
        await market_svc.create_purchase(
            db, listing_id=listing.id, buyer_org_id=buyer_org.id,
            purchaser=_actor(buyer_user), payment_method="credit",
            idempotency_key=f"fx-{ULID()}")
    assert e.value.code == "LISTING_NOT_PURCHASABLE" and e.value.status_code == 409

    await pricing_svc.create_fx_rate(
        db, actor=_actor(buyer_user), base_currency="EUR", quote_currency="USD",
        rate=Decimal("2"), effective_from=datetime.now(UTC) - timedelta(days=1))
    purchase = await market_svc.create_purchase(
        db, listing_id=listing.id, buyer_org_id=buyer_org.id,
        purchaser=_actor(buyer_user), payment_method="credit",
        idempotency_key=f"fx2-{ULID()}")
    assert purchase.currency == "USD"
    assert purchase.amount_minor == 20000                  # €100.00 × 2


@pytest.mark.asyncio
async def test_manual_grant_validation_arcs(db):
    """R273: manual_grant's guards — bad product type/scope 422,
    seat_limited without a positive limit (R44[20]: the seat gate is
    `if grant.seat_limit:` so a missing limit silently uncapped seats),
    unknown tenant 404, and an org outside the tenant (R123[L7]: such a
    grant is silently inert at the install gate)."""
    user = await _mk_user(db)
    org = await _mk_org(db, user)
    pack = await _mk_pack(db, org, user)
    other_user = await _mk_user(db)
    other_org = await _mk_org(db, other_user)          # different tenant
    tenant_id = org.tenant_id

    async def grant(**kw):
        base = dict(product_type="skill_pack", product_id=pack.id,
                    tenant_id=tenant_id, org_id=None, scope="organization",
                    expires_at=None, seat_limit=None, actor=_actor(user))
        base.update(kw)
        return await market_svc.manual_grant(db, **base)

    with pytest.raises(AppError) as e:
        await grant(product_type="spellbook")
    assert e.value.code == "LISTING_INVALID" and e.value.status_code == 422
    with pytest.raises(AppError) as e:
        await grant(scope="galaxy")
    assert e.value.code == "LISTING_INVALID"
    with pytest.raises(AppError) as e:                 # R44[20] both arms
        await grant(scope="seat_limited")
    assert e.value.code == "LISTING_INVALID"
    with pytest.raises(AppError) as e:
        await grant(scope="seat_limited", seat_limit=0)
    assert e.value.code == "LISTING_INVALID"
    with pytest.raises(AppError) as e:
        await grant(tenant_id=str(ULID()))
    assert e.value.code == "TENANT_NOT_FOUND" and e.value.status_code == 404
    with pytest.raises(AppError) as e:                 # R123[L7]
        await grant(org_id=other_org.id)
    assert e.value.code == "LISTING_INVALID"

    ok = await grant(scope="seat_limited", seat_limit=5, org_id=org.id)
    assert ok.status == "active" and ok.seat_limit == 5


@pytest.mark.asyncio
async def test_purchase_blocked_on_inactive_listing_and_delisted_product(db):
    """R314: purchasability gates. A non-active listing (draft/archived) is
    LISTING_NOT_PURCHASABLE 409 — a seller building or retiring a listing must
    not sell. And R44[19]: even an ACTIVE listing must stop selling once its
    underlying product is unpublished or made private (the delisting guard);
    the listing row staying active is not enough."""
    from app.models.skill_pack import PackStatus, PackVisibility, SkillPack

    seller_user = await _mk_user(db)
    buyer_user = await _mk_user(db)
    seller_org = await _mk_org(db, seller_user)
    buyer_org = await _mk_org(db, buyer_user)
    listing = await _mk_listing(db, seller_org, seller_user)
    buyer_tenant = await db.get(TenantAccount, buyer_org.tenant_id)
    await credit_svc.top_up(db, buyer_tenant.id, "USD", 50000, actor=_actor(buyer_user))

    async def buy():
        return await market_svc.create_purchase(
            db, listing_id=listing.id, buyer_org_id=buyer_org.id,
            purchaser=_actor(buyer_user), payment_method="credit",
            idempotency_key=f"r314-{ULID()}")

    # draft listing → 409
    listing.status = "draft"
    await db.flush()
    with pytest.raises(AppError) as e:
        await buy()
    assert e.value.code == "LISTING_NOT_PURCHASABLE" and e.value.status_code == 409

    # archived listing → 409
    listing.status = "archived"
    await db.flush()
    with pytest.raises(AppError) as e:
        await buy()
    assert e.value.code == "LISTING_NOT_PURCHASABLE"

    # active listing but the PRODUCT was unpublished → still blocked (R44[19])
    listing.status = "active"
    pack = await db.get(SkillPack, listing.product_id)
    pack.status = PackStatus.DRAFT
    await db.flush()
    with pytest.raises(AppError) as e:
        await buy()
    assert e.value.code == "LISTING_NOT_PURCHASABLE"

    # product re-published but made PRIVATE → still blocked (visibility gate)
    pack.status = PackStatus.PUBLISHED
    pack.visibility = PackVisibility.PRIVATE
    await db.flush()
    with pytest.raises(AppError) as e:
        await buy()
    assert e.value.code == "LISTING_NOT_PURCHASABLE"

    # published + unlisted → sells again
    pack.visibility = PackVisibility.UNLISTED
    await db.flush()
    purchase = await buy()
    assert purchase.status == "pending"


def test_grant_rank_ordering_and_equal_seat_width():
    """R338 (mutation survivors): pin _grant_rank's ORDER directly —
    tenant > organization > seat_limited; perpetual > expiring; roomier seat
    cap on ties — and grant_covers_listing_width's equal-width boundary (a
    grant with EXACTLY the listing's seat cap covers; only a SMALLER cap
    fails). Order-preserving constant mutants (scope 2→3, expiry-flag 1→2)
    are equivalent by tuple ordering and intentionally not distinguished."""
    from datetime import UTC, datetime, timedelta

    from app.controlplane.models.marketplace import LicenseGrant, MarketplaceListing

    later = datetime.now(UTC) + timedelta(days=30)

    def g(scope, expires=None, seats=None):
        return LicenseGrant(scope=scope, expires_at=expires, seat_limit=seats)

    tenant_exp = g("tenant", expires=later)
    org_perp = g("organization", seats=999)
    seat_perp = g("seat_limited", seats=999)
    org_exp = g("organization", expires=later)
    seat_5 = g("seat_limited", seats=5)
    seat_9 = g("seat_limited", seats=9)

    ranked = sorted(
        [seat_5, org_exp, tenant_exp, seat_perp, org_perp, seat_9],
        key=market_svc._grant_rank, reverse=True)
    # tenant beats even a perpetual roomy org grant; org beats seat_limited
    # regardless of expiry; roomier seat cap wins inside the seat tier
    assert ranked[0] is tenant_exp
    assert ranked[1] is org_perp and ranked[2] is org_exp
    assert ranked[3] is seat_perp
    assert ranked[4] is seat_9 and ranked[5] is seat_5

    # equal seat width COVERS; one seat short does not
    listing = MarketplaceListing(license_scope="seat_limited", seat_limit=10,
                                 upgrade_policy="all_versions")
    assert market_svc.grant_covers_listing_width(
        g("seat_limited", seats=10), listing) is True
    assert market_svc.grant_covers_listing_width(
        g("seat_limited", seats=9), listing) is False

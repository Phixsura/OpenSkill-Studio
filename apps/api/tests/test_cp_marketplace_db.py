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
        # Drain until quiet (full-suite backlog can exceed one batch)
        for _ in range(30):
            async with AsyncSessionLocal() as db:
                if await process_outbox_once(db) == 0:
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

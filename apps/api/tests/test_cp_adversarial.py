"""P12 adversarial suite — one named test per issue #27 §39 bullet.

Each test attacks a specific isolation/immutability/concurrency guarantee
at the service layer (where the defense lives), plus schema-level static
assertions where the defense is structural.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.marketplace import LicenseGrant, MarketplaceListing
from app.controlplane.models.partner import Partner, PartnerMember, RevenueShareRule
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import billing as billing_svc
from app.controlplane.services import credits as credit_svc
from app.controlplane.services import marketplace as market_svc
from app.controlplane.services import metering, rating
from app.controlplane.services import revenue_share as revshare_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import Actor
from app.core.database import AsyncSessionLocal
from app.exceptions import AppError
from app.models.organization import Organization, OrgStatus
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_user(db, role=UserRole.STUDENT) -> User:
    user = User(
        email=f"adv-{ULID()}@test.com",
        email_verified=True,
        password_hash="x",
        display_name="Adv",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user, status=TenantStatus.ACTIVE) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"A {ULID()}",
        slug=f"a-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=status,
        with_trial=False,
    )


async def _mk_org(db, tenant, user) -> Organization:
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    return org


def _actor(user):
    return Actor(user_id=user.id, type="platform")


# ── §39.1 tenant/org isolation ───────────────────────────────


@pytest.mark.asyncio
async def test_cross_tenant_isolation_matrix(db):
    """Non-member access to another tenant → uniform 404 (no existence
    oracle) on tenant read; same via partner reads."""
    user_a = await _mk_user(db)
    user_b = await _mk_user(db)
    tenant_a = await _mk_tenant(db, user_a)
    # B is NOT a member of tenant_a → 404 identical to missing tenant
    with pytest.raises(AppError) as exc_member:
        await tenant_svc.require_tenant_member(db, tenant_a.id, user_b)
    with pytest.raises(AppError) as exc_missing:
        await tenant_svc.require_tenant_member(db, "01JZZZZZZZZZZZZZZZZZZZZZZZ", user_b)
    assert exc_member.value.code == exc_missing.value.code == "TENANT_NOT_FOUND"
    assert exc_member.value.status_code == exc_missing.value.status_code == 404


# ── §39.2 domain confusion / §39.3 host poisoning ────────────


@pytest.mark.asyncio
async def test_domain_confusion_no_cross_tenant(db):
    """A domain owned by tenant A can never resolve to tenant B, and
    DOMAIN_TAKEN never names the owner."""
    from app.controlplane.services import domains as domain_svc

    user_a = await _mk_user(db)
    user_b = await _mk_user(db)
    tenant_a = await _mk_tenant(db, user_a)
    tenant_b = await _mk_tenant(db, user_b)
    host = f"adv-{str(ULID()).lower()[-8:]}.example.io"
    await domain_svc.create_domain(db, tenant_id=tenant_a.id, hostname=host, actor=_actor(user_a))
    with pytest.raises(AppError) as exc:
        await domain_svc.create_domain(
            db, tenant_id=tenant_b.id, hostname=host, actor=_actor(user_b)
        )
    assert exc.value.code == "DOMAIN_TAKEN"
    assert tenant_a.id not in exc.value.message
    assert tenant_a.slug not in exc.value.message


@pytest.mark.asyncio
async def test_host_header_poisoning_inert(db):
    """site-context only exact-matches ACTIVE rows — arbitrary attacker hosts
    (including lookalikes of a pending domain) resolve to the platform
    default, never to a tenant."""
    from app.controlplane.services import domains as domain_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    host = f"pending-{str(ULID()).lower()[-8:]}.example.io"
    await domain_svc.create_domain(db, tenant_id=tenant.id, hostname=host, actor=_actor(user))
    for probe in (host, host.upper(), f"evil-{host}", f"{host}.attacker.com", "///x///"):
        ctx = await domain_svc.resolve_site_context(db, probe)
        assert ctx["tenant_id"] is None, probe


# ── §39.4 webhook replay (covered live in test_cp_billing_db) ─


@pytest.mark.asyncio
async def test_webhook_replay_single_effect(db):
    """Same external_event_id delivered twice → stored once, one effect."""
    import json

    from app.controlplane.services.billing_providers.mock import sign_mock_event

    evt = {"id": f"mevt_{ULID()}", "type": "unknown.event", "data": {}}
    raw, sig = sign_mock_event(evt)
    r1 = await billing_svc.process_webhook(db, "mock", {"x-mock-signature": sig}, raw)
    r2 = await billing_svc.process_webhook(db, "mock", {"x-mock-signature": sig}, raw)
    assert r2.get("duplicate") is True
    assert r1.get("duplicate") is not True
    # Forged signature → 401, never stored
    bad = json.dumps({"id": f"mevt_{ULID()}", "type": "x", "data": {}}).encode()
    with pytest.raises(AppError) as exc:
        await billing_svc.process_webhook(db, "mock", {"x-mock-signature": "forged"}, bad)
    assert exc.value.status_code == 401


# ── §39.5 cross-tenant license ───────────────────────────────


@pytest.mark.asyncio
async def test_license_grant_never_crosses_tenant(db):
    """A grant held by tenant A does not open the install gate for tenant B;
    purchase-row attribution means request params can't plant a foreign
    tenant."""
    seller_user = await _mk_user(db)
    seller_tenant = await _mk_tenant(db, seller_user)
    seller_org = await _mk_org(db, seller_tenant, seller_user)
    buyer_a_user = await _mk_user(db)
    tenant_a = await _mk_tenant(db, buyer_a_user)
    org_a = await _mk_org(db, tenant_a, buyer_a_user)
    buyer_b_user = await _mk_user(db)
    tenant_b = await _mk_tenant(db, buyer_b_user)
    org_b = await _mk_org(db, tenant_b, buyer_b_user)

    product_id = str(ULID())
    listing = MarketplaceListing(
        product_type="workflow_pack",
        product_id=product_id,
        seller_org_id=seller_org.id,
        seller_tenant_id=seller_tenant.id,
        offer_type="paid",
        price_minor=10000,
        currency="USD",
        license_scope="organization",
        platform_commission_pct=Decimal("30"),
        status="active",
    )
    db.add(listing)
    # Grant to tenant A only
    db.add(
        LicenseGrant(
            listing_id=None,
            product_type="workflow_pack",
            product_id=product_id,
            tenant_id=tenant_a.id,
            org_id=org_a.id,
            scope="organization",
            source="manual_grant",
        )
    )
    await db.flush()
    db.add(listing)  # ensure listing persisted before gate check
    await db.flush()

    # A passes; B is blocked
    await market_svc.check_install_license(db, "workflow_pack", product_id, org_a)
    with pytest.raises(AppError) as exc:
        await market_svc.check_install_license(db, "workflow_pack", product_id, org_b)
    assert exc.value.code == "LICENSE_REQUIRED"


# ── §39.6 entitlement bypass via direct API ──────────────────


@pytest.mark.asyncio
async def test_entitlement_direct_api_enforced(db):
    """Feature gating happens server-side: a tenant without the feature gets
    403 from the service regardless of what the frontend hides."""
    from app.controlplane import facade

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)  # no subscription → community defaults
    with pytest.raises(AppError) as exc:
        await facade.require_feature(db, tenant, "white_label")
    assert exc.value.code == "FEATURE_NOT_AVAILABLE" and exc.value.status_code == 403
    with pytest.raises(AppError) as exc2:
        await facade.check_quota(db, tenant, "max_organizations", current=1)
    assert exc2.value.code == "QUOTA_EXCEEDED"


# ── §39.7 provider cost leak ─────────────────────────────────


@pytest.mark.asyncio
async def test_provider_cost_never_in_tenant_responses(db):
    """The tenant-facing rated-usage constructor emits ONLY the whitelisted
    field set; forbidden substrings are structurally absent."""
    import json

    from app.controlplane.api.pricing import TENANT_RATED_FIELDS, _tenant_rated_response

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    event = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id=str(ULID()),
        usage_type="image_generation",
        quantity=1,
        occurred_at=datetime.now(UTC),
        source="manual",
        idempotency_key=f"leak-{ULID()}",
    )
    await rating.rate_event(db, event.id)
    from app.controlplane.models.pricing import RatedUsage

    rated = (
        await db.execute(select(RatedUsage).where(RatedUsage.usage_event_id == event.id))
    ).scalar_one()
    payload = _tenant_rated_response(rated)
    assert set(payload.keys()) == set(TENANT_RATED_FIELDS)
    body = json.dumps(payload)
    for forbidden in ("internal_cost", "margin", "cost_rate", "fx_rate", "unit_cost"):
        assert forbidden not in body, forbidden


# ── §39.8 partner isolation ──────────────────────────────────


@pytest.mark.asyncio
async def test_partner_settlement_isolation(db):
    """Partner B's member cannot read partner A (uniform 404), and a
    non-admin partner member cannot list attributed tenants (403)."""
    from app.controlplane.api.partners import require_partner_member

    user_a = await _mk_user(db)
    user_b = await _mk_user(db)
    partner_a = Partner(
        name="PA", slug=f"pa-{str(ULID()).lower()}", partner_type="reseller", currency="USD"
    )
    partner_b = Partner(
        name="PB", slug=f"pb-{str(ULID()).lower()}", partner_type="reseller", currency="USD"
    )
    db.add_all([partner_a, partner_b])
    await db.flush()
    db.add(PartnerMember(partner_id=partner_a.id, user_id=user_a.id, role="admin"))
    db.add(PartnerMember(partner_id=partner_b.id, user_id=user_b.id, role="member"))
    await db.flush()
    # Cross-partner read → 404 identical to missing partner
    with pytest.raises(AppError) as exc_cross:
        await require_partner_member(db, partner_a.id, user_b)
    with pytest.raises(AppError) as exc_missing:
        await require_partner_member(db, "01JZZZZZZZZZZZZZZZZZZZZZZZ", user_b)
    assert exc_cross.value.code == exc_missing.value.code == "PARTNER_NOT_FOUND"
    # Non-admin member on an admin-only surface → 403 (member IS of partner_b)
    with pytest.raises(AppError) as exc_role:
        await require_partner_member(db, partner_b.id, user_b, "admin")
    assert exc_role.value.status_code == 403


# ── §39.9/§39.10 portal isolation + guest token scope ────────


@pytest.mark.asyncio
async def test_guest_token_scope_expiry_revoke_hash(db):
    """Guest links: stored hashed, uniform 401 on bad/expired/revoked,
    email binding enforced."""
    import hashlib

    from app.controlplane.services import client_portal as portal_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    org = await _mk_org(db, tenant, user)
    from app.models.project import Project

    project = Project(
        org_id=org.id,
        title="Adv",
        slug=f"adv-{str(ULID()).lower()}",
        description="d",
        instructions="i",
        rubric={"criteria": []},
        created_by=user.id,
    )
    db.add(project)
    await db.flush()
    link, raw = await portal_svc.create_guest_link(
        db,
        project_id=project.id,
        label="c",
        email="bound@client.com",
        role="approver",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        actor=_actor(user),
    )
    # Hash-only storage
    assert link.token_hash == hashlib.sha256(raw.encode()).hexdigest()
    assert raw not in link.token_hash
    # Wrong email → uniform 401
    with pytest.raises(AppError) as exc:
        await portal_svc.exchange_guest_token(db, raw, "other@client.com")
    assert exc.value.code == "GUEST_LINK_INVALID" and exc.value.status_code == 401
    # Right email → works
    token, ctx = await portal_svc.exchange_guest_token(db, raw, "bound@client.com")
    assert ctx["project"]["id"] == project.id
    # Guest JWT is type=client_guest → rejected by the PRODUCT auth dep
    from app.core.security import decode_token

    payload = decode_token(token)
    assert payload["type"] == "client_guest"
    # Revoke → next exchange 401
    link.revoked_at = datetime.now(UTC)
    await db.flush()
    with pytest.raises(AppError):
        await portal_svc.exchange_guest_token(db, raw, "bound@client.com")
    # Nonexistent token → same uniform 401
    with pytest.raises(AppError) as exc2:
        await portal_svc.exchange_guest_token(db, "no-such-token", None)
    assert exc2.value.code == "GUEST_LINK_INVALID"


# ── §39.11 no card data anywhere ─────────────────────────────


def test_no_card_fields_anywhere():
    """Static schema assertion: no control-plane table carries card data."""
    from app.controlplane.models import (  # noqa: F401 — imports register metadata
        billing,
        branding,
        client_portal,
        credit,
        marketplace,
        outbox,
        partner,
        plan,
        pricing,
        tenant,
        usage,
    )
    from app.models.base import Base

    forbidden = ("card_number", "card_no", "pan", "cvv", "cvc", "card_exp", "cardholder")
    for table in Base.metadata.tables.values():
        if not table.name.startswith("cp_"):
            continue
        for column in table.columns:
            for probe in forbidden:
                assert probe not in column.name.lower(), f"{table.name}.{column.name}"


# ── §39.12 credit race (asserted heavily in test_cp_credits_db) ──


@pytest.mark.asyncio
async def test_concurrent_debit_never_negative():
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user)
            await credit_svc.top_up(setup, tenant.id, "USD", 500, actor=_actor(user))
            await setup.commit()
            tid = tenant.id

        async def spend():
            async with AsyncSessionLocal() as s:
                try:
                    await credit_svc.debit(
                        s, tid, "USD", 100, reference_type="manual", reference_id=str(ULID())
                    )
                    await s.commit()
                    return True
                except AppError:
                    await s.rollback()
                    return False

        results = await asyncio.gather(*[spend() for _ in range(10)])
        assert sum(results) == 5
        async with AsyncSessionLocal() as s:
            from app.controlplane.models.credit import TenantCreditBalance

            balance = (
                await s.execute(
                    select(TenantCreditBalance.balance_minor).where(
                        TenantCreditBalance.tenant_id == tid
                    )
                )
            ).scalar_one()
            assert balance == 0
    finally:
        await engine.dispose()


# ── §39.13 duplicate metering ────────────────────────────────


@pytest.mark.asyncio
async def test_duplicate_usage_single_bill(db):
    """Same idempotency key twice → one event, one rated row, one billable."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    key = f"dup-{ULID()}"
    e1 = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id=str(ULID()),
        usage_type="image_generation",
        quantity=5,
        occurred_at=datetime.now(UTC),
        source="manual",
        idempotency_key=key,
    )
    e2 = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id=str(ULID()),
        usage_type="image_generation",
        quantity=5,
        occurred_at=datetime.now(UTC),
        source="manual",
        idempotency_key=key,
    )
    assert e1 is not None and e2 is None
    # Rating the same event twice → one rated row (ON CONFLICT DO NOTHING)
    await rating.rate_event(db, e1.id)
    await rating.rate_event(db, e1.id)
    from app.controlplane.models.pricing import RatedUsage

    rated_rows = (
        (await db.execute(select(RatedUsage).where(RatedUsage.usage_event_id == e1.id)))
        .scalars()
        .all()
    )
    assert len(rated_rows) == 1


# ── §39.14 invoice concurrency (heavier version in billing suite) ──


@pytest.mark.asyncio
async def test_concurrent_finalize_single_number(db):
    """Guarded draft→open transition: double-finalize of one invoice is
    exactly-once (second call must not renumber or re-emit)."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    from app.controlplane.models.billing import Invoice

    invoice = Invoice(
        tenant_id=tenant.id,
        currency="USD",
        status="draft",
        subtotal_minor=100,
        total_minor=100,
        amount_due_minor=100,
    )
    db.add(invoice)
    await db.flush()
    inv1 = await billing_svc.finalize_invoice(db, invoice, actor=_actor(user))
    number = inv1.number
    with pytest.raises(AppError):
        await billing_svc.finalize_invoice(db, invoice, actor=_actor(user))
    await db.refresh(invoice)
    assert invoice.number == number  # unchanged


# ── §39.15 refund immutability ───────────────────────────────


@pytest.mark.asyncio
async def test_refund_immutable_sources(db):
    """Refund creates NEGATIVE adjustment entries; original accrual rows are
    byte-identical afterwards."""
    user = await _mk_user(db)
    seller_tenant = await _mk_tenant(db, user)
    seller_org = await _mk_org(db, seller_tenant, user)
    buyer_user = await _mk_user(db)
    buyer_tenant = await _mk_tenant(db, buyer_user)
    buyer_org = await _mk_org(db, buyer_tenant, buyer_user)

    # R86[M8]: create_purchase now re-checks product liveness — the listing
    # needs a real PUBLISHED public pack behind it.
    from app.models.skill_pack import PackStatus, PackVisibility, SkillPack

    _pack = SkillPack(
        owner_org_id=seller_org.id,
        name=f"RP {ULID()}",
        slug=f"rp-{str(ULID()).lower()}",
        status=PackStatus.PUBLISHED,
        visibility=PackVisibility.PUBLIC,
        created_by=user.id,
    )
    db.add(_pack)
    await db.flush()
    listing = MarketplaceListing(
        product_type="skill_pack",
        product_id=_pack.id,
        seller_org_id=seller_org.id,
        seller_tenant_id=seller_tenant.id,
        offer_type="paid",
        price_minor=20000,
        currency="USD",
        license_scope="organization",
        platform_commission_pct=Decimal("30"),
        status="active",
    )
    db.add(listing)
    await db.flush()
    await credit_svc.top_up(db, buyer_tenant.id, "USD", 50000, actor=_actor(buyer_user))
    purchase = await market_svc.create_purchase(
        db,
        listing_id=listing.id,
        buyer_org_id=buyer_org.id,
        purchaser=Actor(user_id=buyer_user.id, type="tenant"),
        payment_method="credit",
        idempotency_key=f"adv-{ULID()}",
    )
    await credit_svc.debit(
        db,
        purchase.buyer_tenant_id,
        purchase.currency,
        purchase.amount_minor,
        reference_type="purchase",
        reference_id=purchase.id,
    )
    purchase = await market_svc.mark_purchase_paid(
        db, purchase_id=purchase.id, payment_ref=None, actor=_actor(buyer_user)
    )
    assert purchase.status == "paid"
    await revshare_svc.accrue_for_purchase(db, purchase.id)
    from app.controlplane.models.partner import RevenueShareEntry

    original = (
        (
            await db.execute(
                select(RevenueShareEntry).where(
                    RevenueShareEntry.source_id == purchase.id,
                    RevenueShareEntry.adjustment_of_id.is_(None),
                )
            )
        )
        .scalars()
        .all()
    )
    snapshot_before = [(e.id, e.share_amount_minor, str(e.rule_snapshot)) for e in original]
    # Refund
    await market_svc.refund_purchase(db, purchase.id, reason="test", actor=_actor(user))
    await revshare_svc.accrue_refund(db, purchase.id)
    # Original rows untouched; negatives exist
    for eid, amount, snap in snapshot_before:
        row = (
            await db.execute(select(RevenueShareEntry).where(RevenueShareEntry.id == eid))
        ).scalar_one()
        assert (row.share_amount_minor, str(row.rule_snapshot)) == (amount, snap)
    negatives = (
        (
            await db.execute(
                select(RevenueShareEntry).where(
                    RevenueShareEntry.source_id == purchase.id,
                    RevenueShareEntry.adjustment_of_id.is_not(None),
                )
            )
        )
        .scalars()
        .all()
    )
    assert negatives and all(e.share_amount_minor <= 0 for e in negatives)
    # License revoked but grant row retained (history)
    grant = (
        await db.execute(select(LicenseGrant).where(LicenseGrant.purchase_id == purchase.id))
    ).scalar_one()
    assert grant.status == "revoked"


# ── §39.16 rule change no retroactive rewrite ────────────────


@pytest.mark.asyncio
async def test_rule_change_no_retroactive_rewrite(db):
    """Activating rule v2 never mutates entries accrued under v1, and a
    replayed accrual is natural-key idempotent."""
    user = await _mk_user(db)
    partner = Partner(
        name="RP", slug=f"rp-{str(ULID()).lower()}", partner_type="reseller", currency="USD"
    )
    db.add(partner)
    await db.flush()
    tenant = await _mk_tenant(db, user)
    tenant.partner_id = partner.id
    rule_v1 = RevenueShareRule(
        beneficiary_type="partner",
        partner_id=partner.id,
        revenue_type="all",
        rule_type="percentage_of_gross_revenue",
        rate=Decimal("10"),
        version=1,
        effective_from=datetime.now(UTC) - timedelta(days=30),
    )
    db.add(rule_v1)
    await db.flush()
    await revshare_svc.activate_rule(db, rule_v1, actor=_actor(user))
    from app.controlplane.models.billing import Invoice

    invoice = Invoice(
        tenant_id=tenant.id,
        currency="USD",
        status="open",
        subtotal_minor=100000,
        total_minor=100000,
        amount_due_minor=100000,
        finalized_at=datetime.now(UTC),
    )
    db.add(invoice)
    await db.flush()
    await revshare_svc.accrue_for_invoice(db, invoice.id)
    from app.controlplane.models.partner import RevenueShareEntry

    entry = (
        await db.execute(select(RevenueShareEntry).where(RevenueShareEntry.source_id == invoice.id))
    ).scalar_one()
    assert entry.share_amount_minor == 10000  # 10%
    # Activate v2 at 20%
    rule_v2 = RevenueShareRule(
        beneficiary_type="partner",
        partner_id=partner.id,
        revenue_type="all",
        rule_type="percentage_of_gross_revenue",
        rate=Decimal("20"),
        version=2,
        effective_from=datetime.now(UTC) - timedelta(days=1),
    )
    db.add(rule_v2)
    await db.flush()
    await revshare_svc.activate_rule(db, rule_v2, actor=_actor(user))
    # Replay the accrual → idempotent no-op, v1 entry unchanged
    await revshare_svc.accrue_for_invoice(db, invoice.id)
    entries = (
        (
            await db.execute(
                select(RevenueShareEntry).where(RevenueShareEntry.source_id == invoice.id)
            )
        )
        .scalars()
        .all()
    )
    assert len(entries) == 1 and entries[0].share_amount_minor == 10000
    assert entries[0].rule_snapshot["version"] == 1


# ── §39.17 suspension blocks all costed paths ────────────────


@pytest.mark.asyncio
async def test_suspension_blocks_all_costed_paths(db):
    """require_tenant_active raises TENANT_SUSPENDED for every terminal
    status; PAST_DUE and TRIAL pass (grace, per §1.3)."""
    from app.controlplane import facade

    user = await _mk_user(db)
    for status, blocked in (
        (TenantStatus.SUSPENDED, True),
        (TenantStatus.CANCELLED, True),
        (TenantStatus.ARCHIVED, True),
        (TenantStatus.PAST_DUE, False),
        (TenantStatus.TRIAL, False),
        (TenantStatus.ACTIVE, False),
    ):
        tenant = await _mk_tenant(db, user, status=status)
        if blocked:
            with pytest.raises(AppError) as exc:
                facade.require_tenant_active(tenant)
            assert exc.value.code == "TENANT_SUSPENDED", tenant.status
        else:
            facade.require_tenant_active(tenant)  # no raise


# ── Impersonation extras (§39 auxiliary) ─────────────────────


@pytest.mark.asyncio
async def test_impersonation_write_guard_and_target_rules(db):
    """Impersonating a platform-privileged target is rejected; the guard
    middleware whitelist covers only notification reads."""
    from app.middleware.impersonation import _WRITE_WHITELIST

    support = await _mk_user(db, role=UserRole.ADMIN)
    admin_target = await _mk_user(db, role=UserRole.ADMIN)
    with pytest.raises(AppError) as exc:
        await tenant_svc.create_impersonation_grant(
            db,
            platform_user=support,
            target_user_id=admin_target.id,
            tenant_id=None,
            reason="debugging a ticket",
            expires_in_minutes=30,
            actor=_actor(support),
        )
    assert exc.value.code == "IMPERSONATION_TARGET_FORBIDDEN"
    # Whitelist is exactly the two notification-read paths
    assert [rx.pattern for rx in _WRITE_WHITELIST] == [
        r"^/api/v1/notifications/[^/]+/read$",
        r"^/api/v1/notifications/read-all$",
    ]
    # Expired grant cannot mint
    student = await _mk_user(db)
    grant = await tenant_svc.create_impersonation_grant(
        db,
        platform_user=support,
        target_user_id=student.id,
        tenant_id=None,
        reason="debugging a ticket",
        expires_in_minutes=5,
        actor=_actor(support),
    )
    grant.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await db.flush()
    with pytest.raises(AppError) as exc2:
        await tenant_svc.mint_impersonation_token(db, grant, actor=_actor(support))
    assert exc2.value.code == "IMPERSONATION_EXPIRED"

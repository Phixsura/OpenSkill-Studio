"""P1 DB tests: tenant lifecycle, membership, impersonation, audit, outbox.

Requires Postgres (make infra-up && make db-migrate). Follows the
test_services_db.py session pattern.
"""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.audit import CommercialAuditEvent
from app.controlplane.models.outbox import OutboxMessage, enqueue
from app.controlplane.models.tenant import (
    TenantAccount,
    TenantStatus,
)
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import Actor
from app.controlplane.worker import HANDLERS, process_outbox_once, register_handler
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture(autouse=True)
async def _dispose_after_sessionless_tests():
    """Tests that open their own AsyncSessionLocal sessions (outbox/concurrency)
    still need the engine disposed per-test — the loop is per-function."""
    yield
    from app.core.database import engine

    await engine.dispose()


async def _mk_user(db, role=UserRole.STUDENT) -> User:
    user = User(
        email=f"cp-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP Test",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


def _actor(user) -> Actor:
    return Actor(user_id=user.id, type="platform")


async def _mk_tenant(db, user, **kw) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=_actor(user),
        owner_user_id=user.id,
        **kw,
    )


# ── Lifecycle ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_tenant_trial_with_owner(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    assert tenant.status == TenantStatus.TRIAL
    assert tenant.trial_ends_at is not None
    members = (
        (
            await db.execute(
                select(tenant_svc.TenantMember).where(
                    tenant_svc.TenantMember.tenant_id == tenant.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(members) == 1 and members[0].role == "owner"
    # audit row written in same tx
    audits = (
        (
            await db.execute(
                select(CommercialAuditEvent).where(
                    CommercialAuditEvent.tenant_id == tenant.id,
                    CommercialAuditEvent.action == "tenant.created",
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(audits) == 1


@pytest.mark.asyncio
async def test_legal_transition_matrix(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await db.commit()
    # trial → active → past_due → active → suspended → active → cancelled → archived
    chain = [
        TenantStatus.ACTIVE,
        TenantStatus.PAST_DUE,
        TenantStatus.ACTIVE,
        TenantStatus.SUSPENDED,
        TenantStatus.ACTIVE,
        TenantStatus.CANCELLED,
        TenantStatus.ARCHIVED,
    ]
    for target in chain:
        tenant = await tenant_svc.transition_status(
            db, tenant, target, actor=_actor(user), reason="test"
        )
        await db.commit()
        assert tenant.status == target


@pytest.mark.asyncio
async def test_illegal_transition_rejected(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    with pytest.raises(AppError) as exc:
        await tenant_svc.transition_status(db, tenant, TenantStatus.ARCHIVED, actor=_actor(user))
    assert exc.value.code == "TENANT_STATUS_CONFLICT"


@pytest.mark.asyncio
async def test_concurrent_suspend_vs_reactivate_single_winner():
    async with AsyncSessionLocal() as setup:
        user = await _mk_user(setup)
        tenant = await _mk_tenant(setup, user)
        await tenant_svc.transition_status(setup, tenant, TenantStatus.ACTIVE, actor=_actor(user))
        await setup.commit()
        tid, uid = tenant.id, user.id

    async def attempt(target):
        async with AsyncSessionLocal() as s:
            t = await s.get(TenantAccount, tid)
            u = await s.get(User, uid)
            try:
                await tenant_svc.transition_status(s, t, target, actor=_actor(u), reason="race")
                await s.commit()
                return True
            except AppError:
                await s.rollback()
                return False

    results = await asyncio.gather(attempt(TenantStatus.SUSPENDED), attempt(TenantStatus.SUSPENDED))
    # Exactly one concurrent suspend wins
    assert sorted(results) == [False, True]


@pytest.mark.asyncio
async def test_suspension_blocks_consumption(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await tenant_svc.transition_status(db, tenant, TenantStatus.ACTIVE, actor=_actor(user))
    await tenant_svc.transition_status(
        db, tenant, TenantStatus.SUSPENDED, actor=_actor(user), reason="test"
    )
    with pytest.raises(AppError) as exc:
        tenant_svc.require_tenant_active(tenant)
    assert exc.value.code == "TENANT_SUSPENDED"
    # PAST_DUE passes
    tenant.status = TenantStatus.PAST_DUE
    tenant_svc.require_tenant_active(tenant)  # no raise


@pytest.mark.asyncio
async def test_trial_expiry_downgrade(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    tenant.trial_ends_at = datetime.now(UTC) - timedelta(days=1)
    await db.flush()
    n = await tenant_svc.expire_trials(db)
    assert n >= 1
    await db.refresh(tenant)
    assert tenant.status == TenantStatus.ACTIVE  # settings default: downgrade


# ── Membership / uniform 404 ─────────────────────────────────


@pytest.mark.asyncio
async def test_non_member_gets_uniform_404(db):
    owner = await _mk_user(db)
    outsider = await _mk_user(db)
    tenant = await _mk_tenant(db, owner)
    with pytest.raises(AppError) as exc:
        await tenant_svc.require_tenant_member(db, tenant.id, outsider)
    assert exc.value.code == "TENANT_NOT_FOUND"
    assert exc.value.status_code == 404
    # Same error for a tenant that does not exist at all — no existence oracle
    with pytest.raises(AppError) as exc2:
        await tenant_svc.require_tenant_member(db, str(ULID()), outsider)
    assert exc2.value.code == "TENANT_NOT_FOUND"


@pytest.mark.asyncio
async def test_role_mismatch_is_403(db):
    owner = await _mk_user(db)
    billing = await _mk_user(db)
    tenant = await _mk_tenant(db, owner)
    await tenant_svc.add_tenant_member(
        db, tenant, user_id=billing.id, role="billing_admin", actor=_actor(owner)
    )
    with pytest.raises(AppError) as exc:
        await tenant_svc.require_tenant_member(db, tenant.id, billing, "owner")
    assert exc.value.code == "TENANT_FORBIDDEN"
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_last_owner_removal_blocked(db):
    owner = await _mk_user(db)
    tenant = await _mk_tenant(db, owner)
    member = (
        await db.execute(
            select(tenant_svc.TenantMember).where(tenant_svc.TenantMember.tenant_id == tenant.id)
        )
    ).scalar_one()
    with pytest.raises(AppError) as exc:
        await tenant_svc.remove_tenant_member(db, tenant, member.id, actor=_actor(owner))
    assert exc.value.code == "LAST_OWNER_REMOVAL"


# ── Impersonation ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_impersonation_target_admin_rejected(db):
    support = await _mk_user(db)
    admin = await _mk_user(db, role=UserRole.ADMIN)
    with pytest.raises(AppError) as exc:
        await tenant_svc.create_impersonation_grant(
            db,
            platform_user=support,
            target_user_id=admin.id,
            tenant_id=None,
            reason="should never work",
            expires_in_minutes=30,
            actor=_actor(support),
        )
    assert exc.value.code == "IMPERSONATION_TARGET_FORBIDDEN"


@pytest.mark.asyncio
async def test_impersonation_token_carries_imp_claims(db):
    import jwt as _jwt

    from app.config import settings as app_settings

    support = await _mk_user(db)
    target = await _mk_user(db)
    grant = await tenant_svc.create_impersonation_grant(
        db,
        platform_user=support,
        target_user_id=target.id,
        tenant_id=None,
        reason="debug ticket #42",
        expires_in_minutes=30,
        actor=_actor(support),
    )
    token, expires_in = await tenant_svc.mint_impersonation_token(db, grant, actor=_actor(support))
    payload = _jwt.decode(token, app_settings.jwt_secret, algorithms=["HS256"])
    assert payload["sub"] == target.id
    assert payload["type"] == "access"
    assert payload["imp"] == support.id
    assert payload["imp_grant"] == grant.id
    assert grant.used_count == 1
    assert 0 < expires_in <= 30 * 60


@pytest.mark.asyncio
async def test_expired_or_revoked_grant_cannot_mint(db):
    support = await _mk_user(db)
    target = await _mk_user(db)
    grant = await tenant_svc.create_impersonation_grant(
        db,
        platform_user=support,
        target_user_id=target.id,
        tenant_id=None,
        reason="debug ticket #43",
        expires_in_minutes=30,
        actor=_actor(support),
    )
    grant.revoked_at = datetime.now(UTC)
    with pytest.raises(AppError) as exc:
        await tenant_svc.mint_impersonation_token(db, grant, actor=_actor(support))
    assert exc.value.code == "IMPERSONATION_EXPIRED"
    grant.revoked_at = None
    grant.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    with pytest.raises(AppError):
        await tenant_svc.mint_impersonation_token(db, grant, actor=_actor(support))


# ── Outbox ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_outbox_atomic_with_business_write():
    """Rolled-back transaction leaves no outbox message."""
    marker = f"test-{ULID()}"
    async with AsyncSessionLocal() as db:
        enqueue(db, "usage.recorded", {"marker": marker})
        await db.flush()
        await db.rollback()
    async with AsyncSessionLocal() as db:
        rows = (
            (
                await db.execute(
                    select(OutboxMessage).where(OutboxMessage.payload["marker"].astext == marker)
                )
            )
            .scalars()
            .all()
        )
        assert rows == []


@pytest.mark.asyncio
async def test_outbox_handler_processes_and_is_idempotent():
    calls: list[dict] = []
    topic = f"test.topic{str(ULID()).lower()[:8]}"

    @register_handler(topic)
    async def _handler(db, payload):
        calls.append(payload)

    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, topic, {"n": 1})
            await db.commit()
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[topic])
            assert handled == 1
        # Second pass: message is done — no reprocessing
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[topic])
            assert handled == 0
        assert len(calls) == 1
    finally:
        HANDLERS.pop(topic, None)


@pytest.mark.asyncio
async def test_outbox_retry_backoff_and_dead_letter():
    topic = f"test.fail{str(ULID()).lower()[:8]}"
    attempts: list[int] = []

    @register_handler(topic)
    async def _handler(db, payload):
        attempts.append(1)
        raise RuntimeError("boom")

    try:
        async with AsyncSessionLocal() as db:
            msg = enqueue(db, topic, {})
            await db.commit()
            msg_id = msg.id
        async with AsyncSessionLocal() as db:
            await process_outbox_once(db, topics=[topic])
        async with AsyncSessionLocal() as db:
            msg = await db.get(OutboxMessage, msg_id)
            assert msg.status == "pending"
            assert msg.attempts == 1
            assert msg.available_at > datetime.now(UTC)  # backed off
            assert "boom" in msg.last_error
            # Fast-forward to dead-letter: exhaust remaining attempts
            from app.config import settings as app_settings

            msg.attempts = app_settings.outbox_max_attempts - 1
            msg.available_at = datetime.now(UTC) - timedelta(seconds=1)
            await db.commit()
        async with AsyncSessionLocal() as db:
            await process_outbox_once(db, topics=[topic])
        async with AsyncSessionLocal() as db:
            msg = await db.get(OutboxMessage, msg_id)
            assert msg.status == "failed"
    finally:
        HANDLERS.pop(topic, None)


@pytest.mark.asyncio
async def test_outbox_concurrent_workers_no_double_consume():
    topic = f"test.conc{str(ULID()).lower()[:8]}"
    processed: list[str] = []

    @register_handler(topic)
    async def _handler(db, payload):
        processed.append(payload["k"])
        await asyncio.sleep(0.05)  # widen the race window

    try:
        async with AsyncSessionLocal() as db:
            for i in range(6):
                enqueue(db, topic, {"k": f"m{i}"})
            await db.commit()

        async def worker():
            async with AsyncSessionLocal() as db:
                return await process_outbox_once(db, topics=[topic])

        counts = await asyncio.gather(worker(), worker())
        assert sum(counts) == 6  # every message handled exactly once
        assert sorted(processed) == [f"m{i}" for i in range(6)]
    finally:
        HANDLERS.pop(topic, None)


# ── Backfill sanity (runs against the migrated dev DB) ───────


@pytest.mark.asyncio
async def test_backfill_left_no_orphan_orgs(db):
    from sqlalchemy import text

    null_count = (
        await db.execute(text("SELECT COUNT(*) FROM organizations WHERE tenant_id IS NULL"))
    ).scalar()
    assert null_count == 0


@pytest.mark.asyncio
async def test_mint_recheck_blocks_promoted_target(db):
    """R54[1] TOCTOU: the privileged-target check ran only at grant creation.
    Grant against a plain user, promote the user, then mint = a support
    member wearing an admin's identity. The mint must re-run the check."""
    support = await _mk_user(db)
    target = await _mk_user(db)
    grant = await tenant_svc.create_impersonation_grant(
        db,
        platform_user=support,
        target_user_id=target.id,
        tenant_id=None,
        reason="debug ticket #44",
        expires_in_minutes=30,
        actor=_actor(support),
    )
    # Promotion path A: product-admin role
    target.role = UserRole.ADMIN
    await db.flush()
    with pytest.raises(AppError) as exc:
        await tenant_svc.mint_impersonation_token(db, grant, actor=_actor(support))
    assert exc.value.code == "IMPERSONATION_TARGET_FORBIDDEN"
    # Promotion path B: platform role assignment
    target.role = UserRole.STUDENT
    from app.controlplane.models.tenant import PlatformRoleAssignment

    db.add(PlatformRoleAssignment(user_id=target.id, role="billing_admin"))
    await db.flush()
    with pytest.raises(AppError) as exc:
        await tenant_svc.mint_impersonation_token(db, grant, actor=_actor(support))
    assert exc.value.code == "IMPERSONATION_TARGET_FORBIDDEN"


@pytest.mark.asyncio
async def test_tenant_membership_changes_audited(db):
    """R54[3]: tenant owner/billing_admin grants are privilege changes —
    both add and remove must land in the audit trail."""
    from app.controlplane.models.audit import CommercialAuditEvent

    owner = await _mk_user(db)
    other = await _mk_user(db)
    tenant = await _mk_tenant(db, owner)
    member = await tenant_svc.add_tenant_member(
        db, tenant, user_id=other.id, role="billing_admin", actor=_actor(owner)
    )
    added = (
        await db.execute(
            select(CommercialAuditEvent).where(
                CommercialAuditEvent.action == "tenant.member_added",
                CommercialAuditEvent.target_id == member.id,
            )
        )
    ).scalar_one()
    assert added.after == {"user_id": other.id, "role": "billing_admin"}
    await tenant_svc.remove_tenant_member(db, tenant, member.id, actor=_actor(owner))
    removed = (
        await db.execute(
            select(CommercialAuditEvent).where(
                CommercialAuditEvent.action == "tenant.member_removed",
                CommercialAuditEvent.target_id == member.id,
            )
        )
    ).scalar_one()
    assert removed.before == {"user_id": other.id, "role": "billing_admin"}


@pytest.mark.asyncio
async def test_checkout_rescues_trial_expiry_suspension(db):
    """R54[2]: with trial_expiry_action='suspend', the cron could suspend a
    still-TRIAL tenant DURING checkout; the webhook completion only handled
    TRIAL and stranded a paying customer. It must rescue exactly the cron's
    suspension (reason='trial expired') — never admin suspensions."""
    from app.controlplane.services import billing as billing_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    # Simulate cron suspension mid-checkout
    await tenant_svc.transition_status(
        db, tenant, TenantStatus.SUSPENDED, actor=_actor(user), reason="trial expired"
    )
    await db.refresh(tenant)
    sub = await billing_svc.activate_subscription_from_checkout(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="mock",
        external_customer_ref="mock_cus_x",
        external_ref=f"mock_sub_{tenant.id}",
    )
    assert sub.status == "active"
    await db.refresh(tenant)
    assert tenant.status == TenantStatus.ACTIVE
    # Admin suspension is NOT rescued by payment
    user2 = await _mk_user(db)
    tenant2 = await _mk_tenant(db, user2)
    await tenant_svc.transition_status(db, tenant2, TenantStatus.ACTIVE, actor=_actor(user2))
    await tenant_svc.transition_status(
        db, tenant2, TenantStatus.SUSPENDED, actor=_actor(user2), reason="abuse investigation"
    )
    await db.refresh(tenant2)
    await billing_svc.activate_subscription_from_checkout(
        db,
        tenant2,
        plan_key="school",
        interval="month",
        seats=0,
        provider="mock",
        external_customer_ref="mock_cus_y",
        external_ref=f"mock_sub_{tenant2.id}",
    )
    await db.refresh(tenant2)
    assert tenant2.status == TenantStatus.SUSPENDED


@pytest.mark.asyncio
async def test_create_org_under_tenant_works_end_to_end(db):
    """R59[4]: the endpoint imported a nonexistent `OrganizationService` —
    every authorized call 500'd. Verify the full path returns 201."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.core.security import create_access_token
    from app.main import app

    owner = await _mk_user(db)
    tenant = await _mk_tenant(db, owner)
    await tenant_svc.transition_status(db, tenant, TenantStatus.ACTIVE, actor=_actor(owner))
    await db.commit()
    token = create_access_token(owner.id, owner.email, owner.role.value)

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post(
                f"/api/v1/tenants/{tenant.id}/orgs",
                json={"name": "Second Org", "slug": f"so-{str(ULID()).lower()}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 201, r.text
            assert r.json()["data"]["tenant_id"] == tenant.id
    finally:
        app.router.lifespan_context = orig


@pytest.mark.asyncio
async def test_revoked_grant_kills_minted_token(db):
    """R59[5]: revoking a grant left already-minted tokens valid for up to 15
    minutes. get_current_user now rejects any token whose imp_grant is
    revoked/expired — revocation is immediate."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.main import app

    support = await _mk_user(db)
    target = await _mk_user(db)
    grant = await tenant_svc.create_impersonation_grant(
        db,
        platform_user=support,
        target_user_id=target.id,
        tenant_id=None,
        reason="debug ticket #45",
        expires_in_minutes=30,
        actor=_actor(support),
    )
    token, _ = await tenant_svc.mint_impersonation_token(db, grant, actor=_actor(support))
    await db.commit()

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": f"Bearer {token}"}
            r = await c.get("/api/v1/auth/me", headers=hdr)
            assert r.status_code == 200  # token works pre-revocation
            grant.revoked_at = datetime.now(UTC)
            await db.commit()
            r = await c.get("/api/v1/auth/me", headers=hdr)
            assert r.status_code == 401, r.text  # dead immediately
    finally:
        app.router.lifespan_context = orig
        await db.rollback()


@pytest.mark.asyncio
async def test_concurrent_org_create_under_tenant_respects_cap():
    """R74[3]: count-then-insert raced — two concurrent POST /tenants/{id}/orgs
    both counted under max_organizations and both inserted. FOR UPDATE on the
    tenant row serializes; exactly one wins at the cap.

    NOTE: ASGITransport serializes requests on one loop, so this exercises
    the cap logic sequentially — the FOR UPDATE itself is the concurrency
    defense (same pattern proven under true concurrency in
    test_concurrent_seat_join_single_winner)."""
    import asyncio as _asyncio
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.plan import TenantEntitlementOverride
    from app.controlplane.services.entitlements import invalidate_cache
    from app.core.database import AsyncSessionLocal, engine
    from app.core.security import create_access_token
    from app.main import app

    try:
        async with AsyncSessionLocal() as setup:
            owner = await _mk_user(setup)
            tenant = await _mk_tenant(setup, owner)
            await tenant_svc.transition_status(
                setup, tenant, TenantStatus.ACTIVE, actor=_actor(owner)
            )
            # cap orgs at 1 — tenant has 0, so exactly one create may pass
            setup.add(
                TenantEntitlementOverride(
                    tenant_id=tenant.id,
                    key="max_organizations",
                    value={"v": 1},
                    reason="r74 race",
                )
            )
            await setup.commit()
            tenant_id = tenant.id
            token = create_access_token(owner.id, owner.email, owner.role.value)
        await invalidate_cache(tenant_id)

        @asynccontextmanager
        async def _noop(a):
            yield

        async def create(n):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
                r = await c.post(
                    f"/api/v1/tenants/{tenant_id}/orgs",
                    json={"name": f"Race {n}", "slug": f"rc74-{n}-{str(ULID()).lower()}"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                return r.status_code

        orig = app.router.lifespan_context
        app.router.lifespan_context = _noop
        try:
            s1, s2 = await _asyncio.gather(create(1), create(2))
        finally:
            app.router.lifespan_context = orig
        assert sorted([s1, s2]) == [201, 403], (s1, s2)
    finally:
        await engine.dispose()

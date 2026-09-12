"""P1 DB tests: tenant lifecycle, membership, impersonation, audit, outbox.

Requires Postgres (make infra-up && make db-migrate). Follows the
test_services_db.py session pattern.

R514 mutation sweep of require_tenant_active/transition_status/expire_trials/
has_platform_role/remove_tenant_member: 21/25 killed by the pre-existing
suite; 2 more killed by new tests (multi-role has_platform_role limit(1),
409 status class on LAST_OWNER_REMOVAL); 2 equivalents:
- expire_trials `limit: int = 500` -> 501: cron batch-size default — any
  positive batch converges over rounds, no behavioral contract.
- `trial_ends_at < now` -> `<=`: clock-instant boundary (a trial ending at
  the exact sweep instant expires one cron round later).
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

    # R134 follow-up: a preceding file can leave pool connections bound to its
    # (now closed) event loop — the first checkout here then dies with
    # "Event loop is closed". Abandon any stale pool without touching the
    # dead-loop connections (close=False), then open fresh ones on this loop.
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture(autouse=True)
async def _dispose_after_sessionless_tests():
    """Tests that open their own AsyncSessionLocal sessions (outbox/concurrency)
    still need the engine disposed per-test — the loop is per-function."""
    yield
    # R132: the outbox tests here COMMIT test.* rows into the shared dev DB —
    # leaked pending rows filled poll batches as handled=0 and broke the e2e
    # drain's early-break. Purge at the source.
    from sqlalchemy import text as _text

    from app.core.database import engine

    async with AsyncSessionLocal() as s:
        await s.execute(_text("DELETE FROM cp_outbox WHERE topic LIKE 'test.%'"))
        await s.commit()
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
        # R339 (mutation survivors): suspension bookkeeping is exclusive to
        # the SUSPENDED target — set (with the reason) on suspend, cleared on
        # reactivate, untouched by every other transition.
        await db.refresh(tenant)
        if target == TenantStatus.SUSPENDED:
            assert tenant.suspended_at is not None
            assert tenant.suspension_reason == "test"
        else:
            assert tenant.suspended_at is None and tenant.suspension_reason is None

    # R339: reactivation from suspension writes the dedicated audit action
    from sqlalchemy import select as _sel

    from app.controlplane.models.audit import CommercialAuditEvent

    actions = (
        await db.execute(
            _sel(CommercialAuditEvent.action).where(
                CommercialAuditEvent.tenant_id == tenant.id))
    ).scalars().all()
    assert "tenant.suspended" in actions
    # EXACTLY one reactivation in the chain (suspended→active); the other
    # →ACTIVE transitions (trial→, past_due→) are plain status_changed
    assert actions.count("tenant.reactivated") == 1


@pytest.mark.asyncio
async def test_illegal_transition_rejected(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    with pytest.raises(AppError) as exc:
        await tenant_svc.transition_status(db, tenant, TenantStatus.ARCHIVED, actor=_actor(user))
    assert exc.value.code == "TENANT_STATUS_CONFLICT"
    assert exc.value.status_code == 409  # R339


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
    assert exc.value.status_code == 409  # conflict class, not client-input


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


@pytest.mark.asyncio
async def test_noop_timezone_patch_does_not_poison_tz_gate(db):
    """R129[M6]: a settings form that round-trips the UNCHANGED timezone in a
    prior PATCH must not trip the 30-day tz-change gate — only rows where the
    value actually changed (after != before) count."""
    from httpx import ASGITransport, AsyncClient

    from app.core.security import create_access_token
    from app.main import app

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await db.commit()  # endpoint uses its own session
    token = create_access_token(user.id, user.email, user.role.value)
    hdrs = {"Authorization": f"Bearer {token}"}
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _noop(_):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Day 1: full-object PATCH including the CURRENT timezone (no-op).
        r = await c.patch(
            f"/api/v1/tenants/{tenant.id}",
            json={"billing_email": "a@b.co", "timezone": tenant.timezone},
            headers=hdrs,
        )
        assert r.status_code == 200, r.text
        # First REAL tz change must not be blocked by the no-op row.
        r = await c.patch(
            f"/api/v1/tenants/{tenant.id}",
            json={"timezone": "America/New_York"},
            headers=hdrs,
        )
        assert r.status_code == 200, r.text
        # A second real change IS blocked (the gate still works).
        r = await c.patch(
            f"/api/v1/tenants/{tenant.id}",
            json={"timezone": "Asia/Tokyo"},
            headers=hdrs,
        )
        assert r.status_code == 422, r.text
        assert "30 days" in r.json()["error"]["message"]


@pytest.mark.asyncio
async def test_concurrent_owner_removals_cannot_reach_zero_owners():
    """R145: the last-owner guard counted owners UNLOCKED — two sessions each
    removing one of the two owners both counted 2 (>1) and both deleted,
    leaving a tenant with ZERO owners (locked out of every owner-gated
    operation forever). The owner rows are now locked (org-side pattern), so
    the loser serializes behind the winner and re-counts 1 → 409."""
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            owner1 = await _mk_user(setup)
            owner2 = await _mk_user(setup)
            tenant = await _mk_tenant(setup, owner1)
            await tenant_svc.add_tenant_member(
                setup, tenant, user_id=owner2.id, role="owner", actor=_actor(owner1)
            )
            members = (
                (
                    await setup.execute(
                        select(tenant_svc.TenantMember).where(
                            tenant_svc.TenantMember.tenant_id == tenant.id
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(members) == 2
            m1_id, m2_id = members[0].id, members[1].id
            await setup.commit()
            tenant_id, actor_id = tenant.id, owner1.id

        outcomes: list[str] = []
        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        try:
            ta = await sa.get(tenant_svc.TenantAccount, tenant_id)
            ua = await sa.get(User, actor_id)
            # A removes owner 1 and HOLDS its tx open (owner rows locked).
            await tenant_svc.remove_tenant_member(sa, ta, m1_id, actor=_actor(ua))

            async def b_remove():
                tb = await sb.get(tenant_svc.TenantAccount, tenant_id)
                ub = await sb.get(User, actor_id)
                try:
                    # B blocks on the locked owner rows until A commits, then
                    # must re-count and see a single remaining owner → 409.
                    await tenant_svc.remove_tenant_member(sb, tb, m2_id, actor=_actor(ub))
                    await sb.commit()
                    outcomes.append("removed")
                except AppError as e:
                    await sb.rollback()
                    outcomes.append(e.code)
                except Exception as exc:  # noqa: BLE001
                    await sb.rollback()
                    outcomes.append(type(exc).__name__)

            b_task = asyncio.create_task(b_remove())
            await asyncio.sleep(0.3)  # B is now blocked on the owner-row lock
            await sa.commit()
            await b_task
        finally:
            await sa.close()
            await sb.close()
        assert outcomes == ["LAST_OWNER_REMOVAL"], outcomes
        async with AsyncSessionLocal() as s:
            remaining = (
                (
                    await s.execute(
                        select(tenant_svc.TenantMember).where(
                            tenant_svc.TenantMember.tenant_id == tenant_id,
                            tenant_svc.TenantMember.role == "owner",
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(remaining) == 1, f"{len(remaining)} owners left — race reached zero"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_expire_trials_isolates_one_bad_tenant(db, monkeypatch):
    """R170: one tenant whose transition_status raises a non-AppError must NOT
    wedge the whole HOURLY trial-expiry cron (the R168/R169 per-item isolation
    class). The healthy expired trial still downgrades; the poison one is left
    for a later pass."""
    poison_owner = await _mk_user(db)
    healthy_owner = await _mk_user(db)
    poison = await _mk_tenant(db, poison_owner)
    healthy = await _mk_tenant(db, healthy_owner)
    poison.trial_ends_at = datetime.now(UTC) - timedelta(days=1)
    healthy.trial_ends_at = datetime.now(UTC) - timedelta(days=1)
    await db.flush()
    poison_id = poison.id

    real_transition = tenant_svc.transition_status

    async def flaky_transition(db_, tenant, to_status, **kw):
        if tenant.id == poison_id:
            raise RuntimeError("simulated transition failure")
        return await real_transition(db_, tenant, to_status, **kw)

    monkeypatch.setattr(tenant_svc, "transition_status", flaky_transition)
    n = await tenant_svc.expire_trials(db)  # must not raise
    await db.flush()
    monkeypatch.undo()

    await db.refresh(poison)
    await db.refresh(healthy)
    assert healthy.status == TenantStatus.ACTIVE, "healthy trial must still expire"
    assert poison.status == TenantStatus.TRIAL, "poison tenant rolled back, left for later"
    assert n >= 1


@pytest.mark.asyncio
async def test_expire_trials_bounded_batch(db):
    """R259: trial expiry drains a bounded oldest-first batch (see the
    credits-side bounded-batch test for the failure mode)."""
    from datetime import timedelta

    for i in range(3):
        t = await _mk_tenant(db, await _mk_user(db))
        t.trial_ends_at = datetime.now(UTC) - timedelta(hours=i + 1)
    await db.flush()
    n1 = await tenant_svc.expire_trials(db, limit=1)
    assert n1 == 1
    n_rest = await tenant_svc.expire_trials(db, limit=500)
    assert n_rest >= 2


@pytest.mark.asyncio
async def test_member_management_reject_arcs(db):
    """R275: add/remove member guards — unknown role 422, unknown user 404,
    duplicate member 409, unknown member id 404, and a member id from
    ANOTHER tenant is a uniform 404 (no cross-tenant existence oracle)."""
    owner = await _mk_user(db)
    tenant = await _mk_tenant(db, owner)
    other_owner = await _mk_user(db)
    other_tenant = await _mk_tenant(db, other_owner)

    with pytest.raises(AppError) as e:
        await tenant_svc.add_tenant_member(
            db, tenant, user_id=owner.id, role="wizard", actor=_actor(owner))
    assert e.value.code == "VALIDATION_ERROR" and e.value.status_code == 422

    with pytest.raises(AppError) as e:
        await tenant_svc.add_tenant_member(
            db, tenant, user_id=str(ULID()), role="billing_admin", actor=_actor(owner))
    assert e.value.status_code == 404

    member2 = await tenant_svc.add_tenant_member(
        db, tenant, user_id=other_owner.id, role="billing_admin", actor=_actor(owner))
    with pytest.raises(AppError) as e:                     # duplicate
        await tenant_svc.add_tenant_member(
            db, tenant, user_id=other_owner.id, role="billing_admin", actor=_actor(owner))
    assert e.value.code == "TENANT_MEMBER_EXISTS" and e.value.status_code == 409

    with pytest.raises(AppError) as e:                     # unknown member id
        await tenant_svc.remove_tenant_member(db, tenant, str(ULID()), actor=_actor(owner))
    assert e.value.status_code == 404

    other_member = (
        await db.execute(
            select(tenant_svc.TenantMember).where(
                tenant_svc.TenantMember.tenant_id == other_tenant.id))
    ).scalar_one()
    with pytest.raises(AppError) as e:                     # cross-tenant id → 404
        await tenant_svc.remove_tenant_member(db, tenant, other_member.id, actor=_actor(owner))
    assert e.value.status_code == 404

    await tenant_svc.remove_tenant_member(db, tenant, member2.id, actor=_actor(owner))


@pytest.mark.asyncio
async def test_update_tenant_http_null_and_tz_ratelimit(db):
    """R295: update_tenant HTTP guards. R99[m20]: an explicit null on a NOT
    NULL column (name/timezone/currency) must 422, not IntegrityError-500 at
    commit. R123[M8]: timezone anchors quota/budget month windows, so a
    change is rate-limited to once per 30 days — a second flip is 422 (a
    same-value round-trip must NOT count, R129[M6])."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.core.security import create_access_token
    from app.main import app

    owner = await _mk_user(db)
    tenant = await _mk_tenant(db, owner)
    await db.commit()
    token = create_access_token(owner.id, owner.email, "student")
    tid = tenant.id

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": f"Bearer {token}"}

            # explicit null on a NOT NULL column → 422 (R99[m20])
            r = await c.patch(f"/api/v1/tenants/{tid}", headers=hdr, json={"name": None})
            assert r.status_code == 422, r.text
            assert r.json()["error"]["code"] == "VALIDATION_ERROR"

            # a same-value timezone round-trip must NOT consume the budget
            same = await c.patch(f"/api/v1/tenants/{tid}", headers=hdr,
                                 json={"timezone": tenant.timezone})
            assert same.status_code == 200, same.text

            # first real change lands
            r1 = await c.patch(f"/api/v1/tenants/{tid}", headers=hdr,
                               json={"timezone": "America/New_York"})
            assert r1.status_code == 200, r1.text

            # second change within 30 days → 422 (quota-window anchor guard)
            r2 = await c.patch(f"/api/v1/tenants/{tid}", headers=hdr,
                               json={"timezone": "Asia/Tokyo"})
            assert r2.status_code == 422, r2.text
            assert "30 days" in r2.json()["error"]["message"]
    finally:
        app.router.lifespan_context = orig


@pytest.mark.asyncio
async def test_impersonation_grant_mint_is_creator_only_revoke_is_any_admin(db):
    """R296: the HTTP-layer isolation on the impersonation surface, with its
    DELIBERATE asymmetry pinned so a future refactor cannot silently flip it:

    - MINT (the privilege-escalation direction — turning a grant into an
      impersonation token) is CREATOR-ONLY: a different platform admin
      minting from admin A's grant gets a uniform 404. This guard lives in
      the endpoint, not the service, so only an HTTP-layer test reaches it;
      a hole here lets any support admin hijack another's grant to act as
      the target user.
    - REVOKE (the defensive direction — disabling a grant) is intentionally
      open to ANY platform admin: incident response must be able to kill a
      suspicious grant created by a possibly-compromised admin. Revoke only
      sets revoked_at and cannot escalate, so this is safe by design."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.tenant import PlatformRoleAssignment
    from app.core.security import create_access_token
    from app.main import app

    admin_a = await _mk_user(db)
    admin_b = await _mk_user(db)
    target = await _mk_user(db)
    db.add_all([
        PlatformRoleAssignment(user_id=admin_a.id, role="platform_support"),
        PlatformRoleAssignment(user_id=admin_b.id, role="platform_support"),
    ])
    grant = await tenant_svc.create_impersonation_grant(
        db, platform_user=admin_a, target_user_id=target.id, tenant_id=None,
        reason="ticket", expires_in_minutes=30, actor=_actor(admin_a))
    await db.commit()
    gid = grant.id
    tok_b = create_access_token(admin_b.id, admin_b.email, admin_b.role.value)

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hb = {"Authorization": f"Bearer {tok_b}"}
            # admin B mints from A's grant → uniform 404
            r = await c.post(f"/api/v1/platform/impersonation-grants/{gid}/token", headers=hb)
            assert r.status_code == 404, r.text
            assert r.json()["error"]["code"] == "IMPERSONATION_GRANT_NOT_FOUND"
            # A's own mint works (proves the grant is live, not just absent
            # for B) — do this BEFORE B revokes, since revoke disables it
            tok_a = create_access_token(admin_a.id, admin_a.email, admin_a.role.value)
            r = await c.post(f"/api/v1/platform/impersonation-grants/{gid}/token",
                             headers={"Authorization": f"Bearer {tok_a}"})
            assert r.status_code == 200, r.text
            # admin B CAN revoke A's grant → 200 (deliberate: defensive
            # incident-response capability; revoke only sets revoked_at)
            r = await c.post(f"/api/v1/platform/impersonation-grants/{gid}/revoke", headers=hb)
            assert r.status_code == 200, r.text
            # once revoked, even the creator can no longer mint from it
            r = await c.post(f"/api/v1/platform/impersonation-grants/{gid}/token",
                             headers={"Authorization": f"Bearer {tok_a}"})
            assert r.status_code != 200, r.text
    finally:
        app.router.lifespan_context = orig


@pytest.mark.asyncio
async def test_tenant_resolution_and_gate_status_codes(db):
    """R339 (mutation survivors): get_tenant_for_org resolves the org's OWN
    tenant (two-tenant setup — a join/where flip returns the other tenant);
    require_tenant_active is a 403; require_tenant_member on a missing
    tenant is a 404; a stale-status transition is a 409."""
    from app.models.organization import Organization, OrgStatus

    user = await _mk_user(db)
    tenant_a = await _mk_tenant(db, user)
    tenant_b = await _mk_tenant(db, user)

    def _org(t, tag):
        return Organization(name=f"O{tag}", slug=f"o{tag}-{str(ULID()).lower()}",
                            status=OrgStatus.ACTIVE, tenant_id=t.id, created_by=user.id)

    org_a, org_b = _org(tenant_a, "a"), _org(tenant_b, "b")
    db.add_all([org_a, org_b])
    await db.flush()
    assert (await tenant_svc.get_tenant_for_org(db, org_a.id)).id == tenant_a.id
    assert (await tenant_svc.get_tenant_for_org(db, org_b.id)).id == tenant_b.id
    with pytest.raises(AppError) as e_no:
        await tenant_svc.get_tenant_for_org(db, str(ULID()))
    assert e_no.value.status_code == 404 and e_no.value.code == "TENANT_NOT_FOUND"

    tenant_a.status = TenantStatus.SUSPENDED
    with pytest.raises(AppError) as e403:
        tenant_svc.require_tenant_active(tenant_a)
    assert e403.value.status_code == 403 and e403.value.code == "TENANT_SUSPENDED"

    with pytest.raises(AppError) as e404:
        await tenant_svc.require_tenant_member(db, str(ULID()), user)
    assert e404.value.status_code == 404

    # stale-status concurrent-conflict arc: a DETACHED snapshot lies about
    # the from-status (mutating the live ORM object would autoflush the lie
    # into the DB and defeat the guard we're testing)
    from types import SimpleNamespace

    await tenant_svc.transition_status(
        db, tenant_b, TenantStatus.ACTIVE, actor=_actor(user))
    stale = SimpleNamespace(id=tenant_b.id, status=TenantStatus.TRIAL)
    with pytest.raises(AppError) as e409:
        await tenant_svc.transition_status(
            db, stale, TenantStatus.ACTIVE, actor=_actor(user))
    assert e409.value.status_code == 409


@pytest.mark.asyncio
async def test_tenants_api_handlers_direct(db):
    """R379: the tenants API handler layer (my_tenants / audit feed) had no
    direct coverage. Pins: (1) my_tenants returns exactly the CALLER's
    memberships with the caller's role attached — another user's tenant and
    another member's role are invisible (the join/where flips leak them);
    (2) the tenant audit feed shows ONLY TENANT_VISIBLE_ACTIONS, honors the
    action filter, and pages with exact offset arithmetic; (3) the org quota
    counts NON-ARCHIVED orgs of THIS tenant; a membership-less user's list
    meta coalesces per_page 0→1. Remaining survivors are FastAPI decorator/
    Query constants plus two filter dims shielded by adjacent gates."""
    from app.controlplane.api.tenants import my_tenants, tenant_audit_events
    from app.controlplane.models.tenant import TenantMember
    from app.controlplane.services.audit import record_audit

    user_a = await _mk_user(db)
    user_b = await _mk_user(db)
    t1 = await _mk_tenant(db, user_a)                  # A owner
    t2 = await _mk_tenant(db, user_b)                  # B's tenant — invisible to A
    db.add(TenantMember(tenant_id=t2.id, user_id=user_a.id,
                        role="billing_admin", created_by=user_b.id))
    await db.flush()

    resp = await my_tenants(user=user_a, db=db)
    mine = {d["id"]: d["my_role"] for d in resp.data}
    assert mine[t1.id] == "owner"
    assert mine[t2.id] == "billing_admin"              # A's OWN role on t2
    resp_b = await my_tenants(user=user_b, db=db)
    ids_b = {d["id"] for d in resp_b.data}
    assert t1.id not in ids_b                          # B never sees A's tenant

    # audit feed: one visible + one platform-internal + one other-action
    for action in ("tenant.updated", "tenant.updated", "branding.updated"):
        await record_audit(db, actor=_actor(user_a), action=action,
                           target_type="tenant", target_id=t1.id,
                           tenant_id=t1.id)
    await record_audit(db, actor=_actor(user_a), action="pricing.cost_rate_created",
                       target_type="cost_rate", target_id=str(ULID()),
                       tenant_id=t1.id)               # platform-internal
    await db.flush()

    feed = await tenant_audit_events(t1.id, action=None, page=1, per_page=50,
                                     user=user_a, db=db)
    actions = [e.action for e in feed.data]
    assert "pricing.cost_rate_created" not in actions  # never tenant-visible
    assert actions.count("tenant.updated") >= 2
    # action filter narrows
    feed_f = await tenant_audit_events(t1.id, action="branding.updated",
                                       page=1, per_page=50, user=user_a, db=db)
    assert {e.action for e in feed_f.data} == {"branding.updated"}
    # exact pagination: per_page 2 of >=4 visible rows → page 2 disjoint
    p1 = await tenant_audit_events(t1.id, action=None, page=1, per_page=2,
                                   user=user_a, db=db)
    p2 = await tenant_audit_events(t1.id, action=None, page=2, per_page=2,
                                   user=user_a, db=db)
    assert len(p1.data) == 2
    assert {e.id for e in p1.data}.isdisjoint({e.id for e in p2.data})
    assert p1.meta.has_more is True
    # exact boundary on the LAST page (total includes tenant.created etc.)
    import math
    last = math.ceil(p1.meta.total / 2)
    p_last = await tenant_audit_events(t1.id, action=None, page=last, per_page=2,
                                       user=user_a, db=db)
    assert p_last.meta.has_more is False
    assert len(p_last.data) >= 1

    # a membership-less user gets an EMPTY list with a sane meta (per_page
    # coalesces 0 → 1; the Or→And mutant emits per_page 0)
    loner = await _mk_user(db)
    empty = await my_tenants(user=loner, db=db)
    assert empty.data == [] and empty.meta.per_page == 1

    # create_org_under_tenant counts NON-ARCHIVED orgs of THIS tenant for the
    # max_organizations quota: an archived org and another tenant's org are
    # not counted (the filter flips block org creation for the wrong tenants)
    from app.controlplane.api.tenants import create_org_under_tenant
    from app.controlplane.schemas.tenant import CreateOrgUnderTenantRequest
    from app.controlplane.services.plans import set_override
    from app.models.organization import Organization, OrgStatus

    await set_override(db, t1.id, "max_organizations", value=1,
                       enforcement="hard", expires_at=None,
                       reason="r379", actor=_actor(user_a))
    db.add_all([
        Organization(name="Arch", slug=f"ar-{str(ULID()).lower()}",
                     status=OrgStatus.ARCHIVED, tenant_id=t1.id, created_by=user_a.id),
        Organization(name="Other", slug=f"ot-{str(ULID()).lower()}",
                     status=OrgStatus.ACTIVE, tenant_id=t2.id, created_by=user_b.id),
    ])
    await db.flush()
    from app.controlplane.services.entitlements import invalidate_cache
    await invalidate_cache(t1.id)
    ok = await create_org_under_tenant(
        t1.id, CreateOrgUnderTenantRequest(name="First Real", slug=f"fr-{str(ULID()).lower()[:10]}"),
        user=user_a, db=db)          # 0 live orgs counted → under the cap of 1
    ok_data = ok if isinstance(ok, dict) else ok.data
    assert (ok_data.get("data") or ok_data)["id"]


async def test_has_platform_role_with_multiple_matching_roles(db):
    """R514 mutation kill: has_platform_role uses .limit(1) before
    scalar_one_or_none — a user holding TWO of the queried roles must still
    resolve True (a limit(2) mutant raises MultipleResultsFound here, i.e. a
    500 on every platform endpoint for multi-role operators)."""
    from app.controlplane.models.tenant import PlatformRoleAssignment
    from app.controlplane.services import tenants as tenant_svc

    user = await _mk_user(db)
    db.add(PlatformRoleAssignment(user_id=user.id, role="platform_support"))
    db.add(PlatformRoleAssignment(user_id=user.id, role="billing_admin"))
    await db.flush()
    assert (
        await tenant_svc.has_platform_role(db, user, "platform_support", "billing_admin")
        is True
    )
    # non-matching query still False for a multi-role user
    assert await tenant_svc.has_platform_role(db, user, "platform_admin") is False

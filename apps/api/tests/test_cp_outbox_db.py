"""P12 outbox infrastructure tests (ADR-014 cross-cutting):
same-tx atomicity, handler idempotency, backoff, dead-letter, SKIP LOCKED."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.outbox import OutboxMessage, enqueue
from app.controlplane.worker import (
    HANDLERS,
    load_handlers,
    process_outbox_once,
    reap_stuck,
    register_handler,
)
from app.core.database import AsyncSessionLocal


@pytest.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture
def test_topic():
    """Register a throwaway handler topic; clean up after."""
    topic = f"test.{str(ULID()).lower()[-8:]}"
    yield topic
    HANDLERS.pop(topic, None)


# ── Atomicity ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enqueue_rolls_back_with_business_tx(db, test_topic):
    """The outbox INSERT lives in the caller's transaction: rollback → gone."""
    enqueue(db, test_topic, {"n": 1})
    await db.flush()
    await db.rollback()
    async with AsyncSessionLocal() as check:
        count = (
            (await check.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic)))
            .scalars()
            .all()
        )
        assert count == []


# ── Processing semantics ─────────────────────────────────────


@pytest.mark.asyncio
async def test_process_success_and_idempotent_handler(test_topic):
    from app.core.database import engine

    calls: list[dict] = []

    @register_handler(test_topic)
    async def _handler(session, payload):  # noqa: ARG001
        calls.append(payload)

    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, test_topic, {"k": "v"})
            await db.commit()
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[test_topic])
            assert handled == 1
        # Second pass: nothing pending → handler not re-invoked
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[test_topic])
            assert handled == 0
        assert calls == [{"k": "v"}]
        async with AsyncSessionLocal() as db:
            msg = (
                await db.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic))
            ).scalar_one()
            assert msg.status == "done" and msg.processed_at is not None
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_failure_backs_off_then_dead_letters(test_topic, monkeypatch):
    from app.config import settings
    from app.core.database import engine

    monkeypatch.setattr(settings, "outbox_max_attempts", 3)

    @register_handler(test_topic)
    async def _handler(session, payload):  # noqa: ARG001
        raise RuntimeError("boom")

    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, test_topic, {})
            await db.commit()

        for attempt in range(1, 4):
            # Make the message due despite exponential backoff
            async with AsyncSessionLocal() as db:
                msg = (
                    await db.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic))
                ).scalar_one()
                msg.available_at = datetime.now(UTC) - timedelta(seconds=1)
                await db.commit()
            async with AsyncSessionLocal() as db:
                await process_outbox_once(db, topics=[test_topic])
            async with AsyncSessionLocal() as db:
                msg = (
                    await db.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic))
                ).scalar_one()
                assert msg.attempts == attempt
                assert "boom" in (msg.last_error or "")
                if attempt < 3:
                    assert msg.status == "pending"
                    # Exponential backoff pushed available_at into the future
                    assert msg.available_at.replace(tzinfo=UTC) > datetime.now(UTC)
                else:
                    assert msg.status == "failed"  # dead-lettered
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_unknown_topic_backs_off_without_burning_attempts():
    from app.core.database import engine

    topic = f"test.unknown.{str(ULID()).lower()[-8:]}"
    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, topic, {})
            await db.commit()
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[topic])
            assert handled == 0
        async with AsyncSessionLocal() as db:
            msg = (
                await db.execute(select(OutboxMessage).where(OutboxMessage.topic == topic))
            ).scalar_one()
            assert msg.status == "pending" and msg.attempts == 0
    finally:
        await engine.dispose()


# ── Concurrency (SKIP LOCKED) ────────────────────────────────


@pytest.mark.asyncio
async def test_dual_worker_no_double_consumption(test_topic):
    """Two concurrent workers over the same batch: each message handled once."""
    from app.core.database import engine

    calls: list[int] = []

    @register_handler(test_topic)
    async def _handler(session, payload):  # noqa: ARG001
        await asyncio.sleep(0.05)  # widen the race window
        calls.append(payload["i"])

    try:
        async with AsyncSessionLocal() as db:
            for i in range(6):
                enqueue(db, test_topic, {"i": i})
            await db.commit()

        async def worker():
            async with AsyncSessionLocal() as session:
                return await process_outbox_once(session, topics=[test_topic])

        results = await asyncio.gather(worker(), worker())
        assert sum(results) == 6  # split between workers, never doubled
        assert sorted(calls) == [0, 1, 2, 3, 4, 5]
    finally:
        await engine.dispose()


# ── R38/C34: DB-error handler must not poison sibling messages ──


@pytest.mark.asyncio
async def test_db_error_handler_does_not_poison_batch():
    """A handler that raises a DB-level IntegrityError (deactivating the
    transaction) must NOT stall its sibling messages in the same batch. The
    per-handler SAVEPOINT rolls back only the failing message's writes; the
    good ones still process and the bad one retries."""
    from app.controlplane.models.audit import CommercialAuditEvent
    from app.core.database import engine

    good = f"test.good.{str(ULID()).lower()[-8:]}"
    dberr = f"test.dberr.{str(ULID()).lower()[-8:]}"
    dup_id = str(ULID())
    processed: list[int] = []

    @register_handler(good)
    async def _good(session, payload):  # noqa: ARG001
        processed.append(payload["n"])

    @register_handler(dberr)
    async def _dberr(session, payload):  # noqa: ARG001
        for _ in range(2):  # second insert violates the PK → IntegrityError
            session.add(
                CommercialAuditEvent(
                    id=dup_id,
                    actor_user_id=None,
                    actor_type="system",
                    action="tenant.created",
                    target_type="x",
                    target_id="y",
                )
            )
            await session.flush()

    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, dberr, {"n": 1})  # fails first, in the same batch
            enqueue(db, good, {"n": 2})
            enqueue(db, good, {"n": 3})
            await db.commit()
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[good, dberr])
        assert handled == 2  # both good messages, despite the earlier DB error
        assert sorted(processed) == [2, 3]
        async with AsyncSessionLocal() as db:
            good_rows = (
                (await db.execute(select(OutboxMessage).where(OutboxMessage.topic == good)))
                .scalars()
                .all()
            )
            bad_row = (
                await db.execute(select(OutboxMessage).where(OutboxMessage.topic == dberr))
            ).scalar_one()
            assert all(r.status == "done" for r in good_rows)
            assert bad_row.status == "pending"  # retries, not lost
            # the failing handler's partial write was rolled back by the savepoint
            dup = await db.get(CommercialAuditEvent, dup_id)
            assert dup is None
    finally:
        HANDLERS.pop(good, None)
        HANDLERS.pop(dberr, None)
        await engine.dispose()


# ── Reaper ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reaper_returns_stuck_processing_to_pending():
    from app.core.database import engine

    topic = f"test.stuck.{str(ULID()).lower()[-8:]}"
    try:
        async with AsyncSessionLocal() as db:
            msg = enqueue(db, topic, {})
            await db.flush()
            msg.status = "processing"
            msg.locked_by = "dead-worker"
            msg.locked_at = datetime.now(UTC) - timedelta(minutes=30)
            await db.commit()
            mid = msg.id
        async with AsyncSessionLocal() as db:
            reaped = await reap_stuck(db, older_than_minutes=10)
            assert reaped >= 1
            await db.commit()
        async with AsyncSessionLocal() as db:
            msg = await db.get(OutboxMessage, mid)
            assert msg.status == "pending" and msg.locked_by is None
    finally:
        await engine.dispose()


def test_all_production_handlers_registered():
    load_handlers()
    expected = {
        "usage.recorded",
        "fx.rate_created",
        "run.terminal",
        "period.close_due",
        "invoice.finalized",
        "purchase.paid",
        "purchase.refunded",
        "credit_note.applied",
        "provision.run",
    }
    assert expected <= set(HANDLERS.keys())


# ── R57: worker resilience + dead-letter ops ─────────────────


@pytest.mark.asyncio
async def test_product_service_rollback_does_not_poison_batch(test_topic):
    """R57[1]: product services (OrgService.create, install_pack, add_item)
    call session.rollback() on IntegrityError. Inside an outbox-handler
    SAVEPOINT that rolled back the ROOT batch transaction — silently WIPING
    every earlier sibling's uncommitted writes in the same batch (handler A
    lands rev-share entries, handler B hits a slug collision → A's money rows
    vanish while A is still marked done). The services now skip the session
    rollback when nested; the AppError unwinds only B's savepoint."""
    from app.models.user import User, UserRole, UserStatus
    from app.services.organization import OrgService

    # Seed a user + an org whose slug we will collide with
    async with AsyncSessionLocal() as setup:
        from app.core.security import hash_password

        user = User(
            email=f"obx-{ULID()}@test.com",
            email_verified=True,
            password_hash=hash_password("Test1234!"),
            display_name="OBX",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
        )
        setup.add(user)
        await setup.flush()
        taken_slug = f"obx-{str(ULID()).lower()}"
        seed_org = await OrgService(setup).create(
            name="Taken", slug=taken_slug, description=None, created_by=user.id
        )
        await setup.commit()
        tenant_id = seed_org.tenant_id

    clean_topic = f"test.{str(ULID()).lower()[-8:]}"
    marker_topic = f"test.{str(ULID()).lower()[-8:]}"

    @register_handler(clean_topic)
    async def clean_handler(db, payload):  # noqa: ARG001
        # A real business write (INSERT) — must survive the sibling's failure.
        enqueue(db, marker_topic, {"landed": True})

    @register_handler(test_topic)
    async def colliding_handler(db, payload):  # noqa: ARG001
        # Reproduces the provisioning path: product service raises
        # IntegrityError→rollback inside the handler savepoint. A slug dupe
        # is caught by create()'s pre-check SELECT, so hit the created_by FK
        # on the ORG insert itself (tenant_id given → no auto-tenant, the
        # wrapped flush is the failing one and the except branch fires).
        await OrgService(db).create(
            name="Dup",
            slug=f"dup-{str(ULID()).lower()}",
            description=None,
            created_by="01JBNOSUCHUSER000000000000",
            tenant_id=tenant_id,
        )

    try:
        # Clean FIRST (strictly earlier available_at — pg now() is
        # tx-constant, so the server default would tie and make the poll
        # order unstable), colliding second: the collision must hit while
        # the clean handler's writes are still uncommitted in the root tx.
        async with AsyncSessionLocal() as db:
            m1 = enqueue(db, clean_topic, {})
            m1.available_at = datetime.now(UTC) - timedelta(seconds=10)
            m2 = enqueue(db, test_topic, {})
            m2.available_at = datetime.now(UTC) - timedelta(seconds=5)
            await db.commit()
        async with AsyncSessionLocal() as db:
            await process_outbox_once(db, topics=[clean_topic, test_topic])
            await db.commit()
        async with AsyncSessionLocal() as check:
            # The clean sibling's business write SURVIVED the collision.
            marker = (
                (
                    await check.execute(
                        select(OutboxMessage).where(OutboxMessage.topic == marker_topic)
                    )
                )
                .scalars()
                .all()
            )
            assert len(marker) == 1, "sibling's write wiped by product-service rollback"
            msgs = {
                m.topic: m
                for m in (
                    (
                        await check.execute(
                            select(OutboxMessage).where(
                                OutboxMessage.topic.in_([test_topic, clean_topic])
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
            }
            assert msgs[clean_topic].status == "done"
            assert msgs[test_topic].status == "pending"
            assert msgs[test_topic].attempts == 1
    finally:
        HANDLERS.pop(clean_topic, None)
        HANDLERS.pop(marker_topic, None)
        from app.core.database import engine

        await engine.dispose()


@pytest.mark.asyncio
async def test_flush_keeps_bucket_when_tenant_has_no_org():
    """R57[3]: the hourly flush deleted the Redis bucket even when the tenant
    had no org to attribute the event to — billable usage silently lost.
    The bucket must survive and land once an org exists."""
    from datetime import timedelta as _td

    import app.core.redis as _redis_mod
    from app.controlplane.models.tenant import TenantStatus
    from app.controlplane.models.usage import UsageEvent
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.audit import Actor
    from app.controlplane.services.metering import flush_api_request_counters
    from app.core.security import hash_password
    from app.models.organization import Organization
    from app.models.user import User, UserRole, UserStatus

    if _redis_mod._redis is not None:
        import contextlib

        with contextlib.suppress(Exception):
            await _redis_mod._redis.aclose()
        _redis_mod._redis = None
    r = _redis_mod.redis_pool()

    async with AsyncSessionLocal() as db:
        user = User(
            email=f"obx2-{ULID()}@test.com",
            email_verified=True,
            password_hash=hash_password("Test1234!"),
            display_name="OBX2",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        await db.flush()
        tenant = await tenant_svc.create_tenant(
            db,
            name=f"NoOrg {ULID()}",
            slug=f"no-{str(ULID()).lower()}",
            actor=Actor(user_id=user.id, type="platform"),
            owner_user_id=user.id,
            status=TenantStatus.ACTIVE,
            with_trial=False,
        )
        await db.commit()
        tenant_id = tenant.id
        user_id = user.id

    # Bucket old enough to pass the 25h delete cutoff — the ONLY thing that
    # may keep it alive is the org-less guard.
    bucket = (datetime.now(UTC) - _td(hours=30)).strftime("%Y%m%d%H")
    key = f"cp:apireq:{tenant_id}:{bucket}"
    await r.set(key, 17, ex=90_000)
    try:
        async with AsyncSessionLocal() as db:
            await flush_api_request_counters(db)
        assert await r.get(key) is not None, "org-less tenant's bucket must survive"
        # Org appears → next flush lands it and may delete the bucket
        async with AsyncSessionLocal() as db:
            db.add(
                Organization(
                    name=f"Late {ULID()}",
                    slug=f"lt-{str(ULID()).lower()}",
                    tenant_id=tenant_id,
                    created_by=user_id,
                )
            )
            await db.commit()
        async with AsyncSessionLocal() as db:
            await flush_api_request_counters(db)
        assert await r.get(key) is None  # landed + old → deleted
        async with AsyncSessionLocal() as db:
            ev = (
                await db.execute(
                    select(UsageEvent).where(
                        UsageEvent.tenant_id == tenant_id,
                        UsageEvent.usage_type == "api_request",
                    )
                )
            ).scalar_one()
            assert int(ev.quantity) == 17
    finally:
        await r.delete(key)
        from app.core.database import engine

        await engine.dispose()


@pytest.mark.asyncio
async def test_failed_outbox_list_and_requeue(test_topic):
    """R57[4]: dead-lettered messages were invisible and unrecoverable. The
    ops endpoints list them and requeue (guarded failed→pending, audited)."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.tenant import PlatformRoleAssignment
    from app.core.security import create_access_token, hash_password
    from app.main import app
    from app.models.user import User, UserRole, UserStatus

    @register_handler(test_topic)
    async def always_fails(db, payload):  # noqa: ARG001
        raise RuntimeError("boom")

    async with AsyncSessionLocal() as db:
        admin = User(
            email=f"obx3-{ULID()}@test.com",
            email_verified=True,
            password_hash=hash_password("Test1234!"),
            display_name="OBX3",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
        )
        db.add(admin)
        await db.flush()
        db.add(PlatformRoleAssignment(user_id=admin.id, role="billing_admin"))
        msg = OutboxMessage(topic=test_topic, payload={"x": 1}, status="failed", attempts=8)
        msg.last_error = "boom"
        db.add(msg)
        await db.commit()
        admin_id, admin_email, admin_role = admin.id, admin.email, admin.role.value
        msg_id = msg.id

    token = create_access_token(admin_id, admin_email, admin_role)

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": f"Bearer {token}"}
            r = await c.get(f"/api/v1/platform/outbox/failed?topic={test_topic}", headers=hdr)
            assert r.status_code == 200, r.text
            ids = [m["id"] for m in r.json()["data"]]
            assert msg_id in ids
            r = await c.post(f"/api/v1/platform/outbox/{msg_id}/requeue", headers=hdr)
            assert r.status_code == 200, r.text
            # Second requeue of the now-pending row → 409 (guarded)
            r = await c.post(f"/api/v1/platform/outbox/{msg_id}/requeue", headers=hdr)
            assert r.status_code == 409
    finally:
        app.router.lifespan_context = orig

    async with AsyncSessionLocal() as check:
        row = await check.get(OutboxMessage, msg_id)
        assert row.status == "pending"
        assert row.attempts == 0 and row.last_error is None
    from app.core.database import engine

    await engine.dispose()

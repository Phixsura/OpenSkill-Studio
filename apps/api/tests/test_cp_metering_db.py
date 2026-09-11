"""P3 DB tests: usage events, idempotency, adjustments, sweeps, emitters."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.outbox import OutboxMessage
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.models.usage import USAGE_TYPES, UsageEvent
from app.controlplane.services import metering
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import Actor
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


async def _mk_user(db) -> User:
    user = User(
        email=f"cp3-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP3",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"M {ULID()}",
        slug=f"m-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )


async def _fresh_redis():
    """redis_pool() is a process singleton whose connections bind to the
    creating test's event loop — reset it so THIS test's loop owns it."""
    import contextlib

    import app.core.redis as _redis_mod

    if _redis_mod._redis is not None:
        with contextlib.suppress(Exception):
            await _redis_mod._redis.aclose()
        _redis_mod._redis = None
    return _redis_mod.redis_pool()


def _now():
    return datetime.now(UTC)


# ── emit_usage ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_emit_usage_writes_event_and_outbox(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    key = f"t-{ULID()}"
    event = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation",
        quantity=3,
        occurred_at=_now(),
        source="manual",
        idempotency_key=key,
    )
    assert event is not None
    assert event.unit == "images"  # canonical unit auto-filled
    outbox = (
        await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "usage.recorded",
                OutboxMessage.payload["usage_event_id"].astext == event.id,
            )
        )
    ).scalar_one()
    assert outbox.status == "pending"


@pytest.mark.asyncio
async def test_emit_usage_idempotent_double_ingest(db):
    """Issue §10 acceptance: duplicate ingestion cannot double-bill."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    key = f"dup-{ULID()}"
    common = dict(
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="llm_output_tokens",
        quantity=500,
        occurred_at=_now(),
        source="manual",
        idempotency_key=key,
    )
    first = await metering.emit_usage(db, **common)
    second = await metering.emit_usage(db, **common)
    assert first is not None
    assert second is None  # duplicate = no-op
    events = (
        (await db.execute(select(UsageEvent).where(UsageEvent.idempotency_key == key)))
        .scalars()
        .all()
    )
    assert len(events) == 1
    outbox_count = (
        (
            await db.execute(
                select(OutboxMessage).where(
                    OutboxMessage.payload["usage_event_id"].astext == first.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(outbox_count) == 1


@pytest.mark.asyncio
async def test_emit_usage_validation(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    base = dict(
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        occurred_at=_now(),
        source="manual",
    )
    with pytest.raises(AppError) as e1:
        await metering.emit_usage(db, usage_type="nope", quantity=1, **base)
    assert e1.value.code == "UNKNOWN_USAGE_TYPE"
    with pytest.raises(AppError) as e2:
        await metering.emit_usage(db, usage_type="workflow_run", quantity=-1, **base)
    assert e2.value.code == "INVALID_QUANTITY"
    with pytest.raises(AppError) as e3:
        await metering.emit_usage(db, usage_type="workflow_run", quantity=float("nan"), **base)
    assert e3.value.code == "INVALID_QUANTITY"
    # R210: unknown usage SOURCE — the L49 guard had no test reaching its
    # reject branch. A bad source (client typo, or a new emitter forgetting
    # to register its source) must 422, not persist an unattributable event.
    base_no_source = {k: v for k, v in base.items() if k != "source"}
    with pytest.raises(AppError) as e4:
        await metering.emit_usage(
            db, usage_type="workflow_run", quantity=1, source="bogus_source", **base_no_source
        )
    assert e4.value.code == "VALIDATION_ERROR"
    # R325: an oversized quantity must 422 at the boundary, not overflow
    # Numeric(18,6) at the INSERT as an asyncpg DataError (no sqlstate → raw
    # 500 on the ingest API; in the workflow step-usage path it escaped the
    # `except AppError` containment and aborted the run's transaction).
    with pytest.raises(AppError) as e5:
        await metering.emit_usage(db, usage_type="workflow_run", quantity="1e15", **base)
    assert e5.value.code == "INVALID_QUANTITY" and e5.value.status_code == 422
    with pytest.raises(AppError) as e6:  # negative overflow via adjustment source
        await metering.emit_usage(
            db, usage_type="workflow_run", quantity=-10**13,
            **{**base, "source": "adjustment"},
        )
    assert e6.value.code == "INVALID_QUANTITY"
    # boundary: the exact column max is recordable
    ok_max = await metering.emit_usage(
        db, usage_type="workflow_run", quantity="999999999999.999999",
        idempotency_key=f"max-{ULID()}", **base
    )
    assert ok_max is not None
    # R331 (mutation survivors): pin the remaining validation semantics.
    # A STRING "Infinity" parses to a non-finite Decimal without being a
    # float instance — the finiteness guard must catch it on the Decimal
    # side alone (PG numeric accepts Infinity since v14: it would STORE).
    with pytest.raises(AppError) as e7:
        await metering.emit_usage(db, usage_type="workflow_run", quantity="Infinity", **base)
    assert e7.value.code == "INVALID_QUANTITY" and e7.value.status_code == 422
    # zero quantity is legal for a non-adjustment source (only NEGATIVE
    # requires an adjustment) — adapters legitimately report 0-usage steps
    ok_zero = await metering.emit_usage(
        db, usage_type="workflow_run", quantity=0,
        idempotency_key=f"zero-{ULID()}", **base
    )
    assert ok_zero is not None
    # metadata=None must store the empty dict, not jsonb null
    ok_meta = await metering.emit_usage(
        db, usage_type="workflow_run", quantity=1, metadata=None,
        idempotency_key=f"meta-{ULID()}", **base
    )
    assert ok_meta is not None and ok_meta.metadata_ == {}
    ok_meta2 = await metering.emit_usage(  # keyless branch stores {} too
        db, usage_type="workflow_run", quantity=1, metadata=None, **base
    )
    assert ok_meta2 is not None and ok_meta2.metadata_ == {}
    # an unparseable STRING quantity → 422 (InvalidOperation branch)
    with pytest.raises(AppError) as e8:
        await metering.emit_usage(db, usage_type="workflow_run", quantity="abc", **base)
    assert e8.value.code == "INVALID_QUANTITY" and e8.value.status_code == 422
    # a STRING "NaN" parses to Decimal NaN without being a float — the
    # finiteness guard must catch it on the Decimal side alone, or the later
    # `qty < 0` comparison raises InvalidOperation (a raw 500)
    with pytest.raises(AppError) as e9:
        await metering.emit_usage(db, usage_type="workflow_run", quantity="NaN", **base)
    assert e9.value.code == "INVALID_QUANTITY" and e9.value.status_code == 422
    # every validation raise is a 422 (not a 4xx-adjacent typo)
    for exc in (e1, e2, e3, e4, e5, e6):
        assert exc.value.status_code == 422
    # positive control: a registered source persists
    ok = await metering.emit_usage(
        db, usage_type="workflow_run", quantity=1, source="manual",
        idempotency_key=f"src-ok-{ULID()}", **base_no_source
    )
    assert ok is not None


@pytest.mark.asyncio
async def test_adjustment_negative_allowed_and_audited(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    original = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation",
        quantity=10,
        occurred_at=_now(),
        source="manual",
        idempotency_key=f"orig-{ULID()}",
    )
    adj = await metering.ingest_adjustment(
        db,
        original_event_id=original.id,
        delta_quantity=-4,
        reason="provider reconciliation: 4 images never delivered",
        actor=Actor(user_id=user.id, type="platform"),
    )
    assert adj.source == "adjustment"
    assert adj.adjustment_of_id == original.id
    assert str(adj.quantity) in ("-4", "-4.000000")
    from app.controlplane.models.audit import CommercialAuditEvent

    audit = (
        (
            await db.execute(
                select(CommercialAuditEvent).where(
                    CommercialAuditEvent.action == "usage.adjusted",
                    CommercialAuditEvent.target_id == original.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(audit) == 1


@pytest.mark.asyncio
async def test_rollback_leaves_no_event_or_outbox():
    """Atomicity: usage + outbox vanish with the business transaction."""
    key = f"atomic-{ULID()}"
    async with AsyncSessionLocal() as db:
        user = await _mk_user(db)
        tenant = await _mk_tenant(db, user)
        await metering.emit_usage(
            db,
            tenant_id=tenant.id,
            org_id="01JFAKEORGFAKEORGFAKEORGFA",
            usage_type="workflow_run",
            quantity=1,
            occurred_at=_now(),
            source="workflow_runtime",
            idempotency_key=key,
        )
        await db.rollback()
    async with AsyncSessionLocal() as db:
        events = (
            (await db.execute(select(UsageEvent).where(UsageEvent.idempotency_key == key)))
            .scalars()
            .all()
        )
        assert events == []
    from app.core.database import engine

    await engine.dispose()


# ── Registry sanity ──────────────────────────────────────────


def test_usage_types_units():
    assert USAGE_TYPES["llm_input_tokens"] == "tokens"
    assert USAGE_TYPES["storage_gb_day"] == "gb_day"
    assert USAGE_TYPES["active_learner_seat"] == "seats"
    assert len(USAGE_TYPES) == 13  # issue Part D §9 full list


# ── Sweeps ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_seat_sweep_idempotent(db):
    """Seat sweep emits per org with active students; rerun emits nothing new."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    owner = await _mk_user(db)
    svc = OrgService(db)
    org = await svc.create(
        name=f"Sweep {ULID()}",
        slug=f"sweep-{str(ULID()).lower()}",
        description=None,
        created_by=owner.id,
    )
    student = await _mk_user(db)
    await svc.add_member(org.id, student.id, OrgRole.STUDENT)
    month = datetime.now(UTC).strftime("%Y-%m")
    n1 = await metering.sweep_seats(db, for_month=month, org_ids=[org.id])
    assert n1 == 1
    await metering.sweep_seats(db, for_month=month, org_ids=[org.id])
    # Rerun: our org's key already exists → not re-emitted
    seat_events = (
        (
            await db.execute(
                select(UsageEvent).where(UsageEvent.idempotency_key == f"seats:{org.id}:{month}")
            )
        )
        .scalars()
        .all()
    )
    assert len(seat_events) == 1
    assert int(seat_events[0].quantity) == 1  # one active student


# ── Mock adapter usage contract ──────────────────────────────


@pytest.mark.asyncio
async def test_mock_adapter_returns_deterministic_usage():
    from app.services.workflow_adapters import MockAdapter

    out = await MockAdapter().execute(
        capability="image_generation",
        model_name="mock-img",
        inputs={"prompt": "cat"},
        config={},
        credentials=None,
        idempotency_key="k",
    )
    assert out["__usage__"] == [{"usage_type": "image_generation", "quantity": 1}]
    out2 = await MockAdapter().execute(
        capability="text_review",
        model_name="mock-t",
        inputs={},
        config={},
        credentials=None,
        idempotency_key="k",
    )
    types = {u["usage_type"] for u in out2["__usage__"]}
    assert types == {"llm_input_tokens", "llm_output_tokens"}


# ── Middleware path classification (pure logic) ──────────────


def test_api_metering_path_classification():
    from app.middleware.api_metering import classify_path

    org_id = "01JBCDEFGHJKMNPQRSTVWXYZ01"
    assert classify_path(f"/api/v1/orgs/{org_id}/projects") == f"org:{org_id}"
    assert classify_path(f"/api/v1/tenants/{org_id}") == f"tenant:{org_id}"
    for path in (
        "/api/v1/platform/tenants",
        "/api/v1/auth/login",
        "/api/v1/health",
        "/api/v1/billing/webhooks/stripe",
        "/api/v1/registry/packs",  # public browsing not attributed
        "/health",
    ):
        assert classify_path(path) is None, path


@pytest.mark.asyncio
async def test_failed_eval_still_meters_token_spend(db):
    """R49[40]: a parse-failed evaluation already consumed real LLM tokens —
    the provider charged for them. The failure branch must emit the token
    usage events (but NOT multimodal_evaluation — no evaluation was produced).
    Previously only the success path metered, so failed evals were free."""
    from unittest.mock import AsyncMock, patch

    from app.core.llm import LLMResponse
    from app.services.evaluation import EvaluationService
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"EF {ULID()}",
        slug=f"ef-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()

    eval_svc = EvaluationService(db)
    await eval_svc.update_eval_settings(org.id, {"enabled": True, "monthly_budget_usd": 100})
    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "EFP",
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
    sub = await proj_svc.create_submission(org.id, proj.id, user.id)
    await proj_svc.submit_draft(sub.id, user.id)
    await db.flush()

    bad = LLMResponse(
        content="not json at all",
        input_tokens=123,
        output_tokens=45,
        model="claude-sonnet-5",
        provider="anthropic",
    )
    with patch("app.services.evaluation.create_llm_client") as mock_create:
        mock_llm = AsyncMock()
        mock_llm.complete = AsyncMock(return_value=bad)
        mock_create.return_value = mock_llm
        task = await eval_svc.trigger_evaluation(org.id, sub.id, "submission_review")
        await db.flush()

    assert task.status.value == "failed"
    events = (
        (await db.execute(select(UsageEvent).where(UsageEvent.evaluation_task_id == task.id)))
        .scalars()
        .all()
    )
    by_type = {e.usage_type: e for e in events}
    assert "llm_input_tokens" in by_type, "input tokens not metered on parse failure"
    assert "llm_output_tokens" in by_type
    assert int(by_type["llm_input_tokens"].quantity) == 123
    assert int(by_type["llm_output_tokens"].quantity) == 45
    # No evaluation was produced — no multimodal_evaluation event
    assert "multimodal_evaluation" not in by_type
    # A UI retry is a NEW spend — its keys must not collide with this one
    # (retries was bumped after emission).
    assert by_type["llm_input_tokens"].idempotency_key == f"eval:{task.id}:0:in"
    assert task.retries == 1


@pytest.mark.asyncio
async def test_flush_keeps_todays_buckets_for_quota_window(db):
    """R53[1]: the hourly flush DELETEd each landed bucket, destroying the
    live day-window the quota middleware MGETs — by late day the sum was
    near-zero and tenants sailed past max_api_requests_day. Flush must land
    the events but keep buckets younger than 25h; only ancient buckets go."""
    from datetime import timedelta

    from app.controlplane.services.metering import flush_api_request_counters

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    from app.models.organization import Organization

    org = Organization(
        name=f"F {ULID()}",
        slug=f"fl-{str(ULID()).lower()}",
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    await db.commit()  # flush_api_request_counters commits per key

    r = await _fresh_redis()
    now = datetime.now(UTC)
    recent_bucket = (now - timedelta(hours=2)).strftime("%Y%m%d%H")
    ancient_bucket = (now - timedelta(hours=30)).strftime("%Y%m%d%H")
    recent_key = f"cp:apireq:{tenant.id}:{recent_bucket}"
    ancient_key = f"cp:apireq:{tenant.id}:{ancient_bucket}"
    await r.set(recent_key, 42, ex=90_000)
    await r.set(ancient_key, 7, ex=90_000)
    try:
        emitted = await flush_api_request_counters(db)
        assert emitted >= 2
        # Recent bucket SURVIVES (still part of someone's current local day)
        assert await r.get(recent_key) is not None, "recent bucket must not be deleted"
        # Ancient bucket is gone
        assert await r.get(ancient_key) is None
        # Both landed as events exactly once; a re-run doesn't double-land
        emitted2 = await flush_api_request_counters(db)
        assert emitted2 == 0
        events = (
            (
                await db.execute(
                    select(UsageEvent).where(
                        UsageEvent.tenant_id == tenant.id,
                        UsageEvent.usage_type == "api_request",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert {int(e.quantity) for e in events} == {42, 7}
    finally:
        await r.delete(recent_key, ancient_key)


def test_local_day_buckets_follow_tenant_timezone():
    """R53[2]: the daily quota window is the tenant-local calendar day mapped
    onto UTC hour buckets — not the UTC day."""
    from app.middleware.api_metering import _local_day_buckets

    # 2026-08-31 23:30 UTC = 2026-09-01 11:30 in Auckland (NZST, UTC+12):
    # Auckland's day spans Aug 31 12:00 UTC .. Sep 1 12:00 UTC.
    now = datetime(2026, 8, 31, 23, 30, tzinfo=UTC)
    nz = _local_day_buckets("Pacific/Auckland", now)
    assert len(nz) == 24
    assert nz[0] == "2026083112"
    assert nz[-1] == "2026090111"
    # UTC tenant: plain UTC day.
    utc = _local_day_buckets("UTC", now)
    assert utc[0] == "2026083100" and utc[-1] == "2026083123"
    # Bad tz falls back to UTC.
    assert _local_day_buckets("Nope/Zone", now) == utc


def test_local_day_buckets_dst_transition_lengths():
    """R113[L4]: a DST-transition local day is 23h (spring-forward) or 25h
    (fall-back), NOT 24 — a fixed 24-hour window under-counts (quota leak)
    or over-counts (double-bill into tomorrow). US/Eastern 2026: DST begins
    Sun Mar 8 (23h), ends Sun Nov 1 (25h)."""
    from app.middleware.api_metering import _local_day_buckets

    # Spring-forward day: 23 hourly buckets.
    spring = _local_day_buckets("America/New_York", datetime(2026, 3, 8, 12, 0, tzinfo=UTC))
    assert len(spring) == 23, f"spring-forward day must be 23h, got {len(spring)}"
    # Fall-back day: 25 hourly buckets.
    fall = _local_day_buckets("America/New_York", datetime(2026, 11, 1, 12, 0, tzinfo=UTC))
    assert len(fall) == 25, f"fall-back day must be 25h, got {len(fall)}"
    # A normal (non-transition) day is exactly 24.
    normal = _local_day_buckets("America/New_York", datetime(2026, 6, 15, 12, 0, tzinfo=UTC))
    assert len(normal) == 24
    # Buckets are contiguous and unique (no gap/overlap regardless of length).
    for buckets in (spring, fall, normal):
        assert len(set(buckets)) == len(buckets)


@pytest.mark.asyncio
async def test_quota_cache_dropped_on_entitlement_invalidation(db):
    """R55[2]: the middleware's cp:apiquota cache was never invalidated —
    plan changes kept 429ing at the old limit for up to 5 minutes.
    invalidate_cache now drops it together with cp:ent."""
    from app.controlplane.services.entitlements import invalidate_cache

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    r = await _fresh_redis()
    quota_key = f"cp:apiquota:{tenant.id}"
    await r.set(quota_key, "10000|UTC", ex=300)
    await invalidate_cache(tenant.id)
    assert await r.get(quota_key) is None


@pytest.mark.asyncio
async def test_entitlement_cache_tombstone_blocks_stale_repopulate(db):
    """R55[1]: invalidate_cache runs BEFORE the mutation's commit — a reader
    racing that window recomputed from the pre-write snapshot and re-cached
    the stale value for the full TTL. The dirty tombstone lets readers
    compute but blocks the cache write until the mutation is safely past."""
    from app.controlplane.services.entitlements import get_effective, invalidate_cache

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    r = await _fresh_redis()
    ent_key = f"cp:ent:{tenant.id}"
    try:
        # Mutation-side: invalidate (tombstone set, cache dropped)
        await invalidate_cache(tenant.id)
        assert await r.get(ent_key) is None
        # Racing reader: computes fine but must NOT re-populate the cache
        eff = await get_effective(db, tenant)
        assert eff.values  # reader still gets a full answer
        assert await r.get(ent_key) is None, "stale re-populate not blocked"
        # After the tombstone expires, caching resumes
        await r.delete(f"cp:entdirty:{tenant.id}")
        await get_effective(db, tenant)
        assert await r.get(ent_key) is not None
    finally:
        await r.delete(ent_key, f"cp:entdirty:{tenant.id}", f"cp:apiquota:{tenant.id}")


@pytest.mark.asyncio
async def test_emit_failure_does_not_poison_completed_eval(db):
    """R77[1]: _emit_usage_events swallowed exceptions WITHOUT a savepoint —
    a DB error during emit left the outer transaction aborted, and the
    caller's next flush raised PendingRollbackError, rolling back a paid
    COMPLETED evaluation. The emissions are now savepoint-isolated."""
    from unittest.mock import AsyncMock, patch

    from app.core.llm import LLMResponse
    from app.models.evaluation import EvaluationTask
    from app.services.evaluation import EvaluationService
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"PZ {ULID()}",
        slug=f"pz-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    eval_svc = EvaluationService(db)
    await eval_svc.update_eval_settings(org.id, {"enabled": True, "monthly_budget_usd": 100})
    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "PZP",
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
    sub = await proj_svc.create_submission(org.id, proj.id, user.id)
    await proj_svc.submit_draft(sub.id, user.id)
    await db.flush()

    good = LLMResponse(
        content=(
            '{"scores":[{"criterion":"Q","score":80,"max_score":100,"feedback":"ok"}],'
            '"overall_feedback":"fine","strengths":[],"improvements":[]}'
        ),
        input_tokens=100,
        output_tokens=50,
        model="claude-sonnet-5",
        provider="anthropic",
    )

    async def poisoned_emit(db_, **kw):
        # Simulate a DB-level failure INSIDE the caller's session: execute
        # broken SQL so the (sub)transaction aborts — exactly what a bad
        # metering write does.
        from sqlalchemy import text as _text

        await db_.execute(_text("SELECT 1/0"))

    with (
        patch("app.services.evaluation.create_llm_client") as mock_create,
        patch("app.controlplane.facade.emit_usage", side_effect=poisoned_emit),
    ):
        mock_llm = AsyncMock()
        mock_llm.complete = AsyncMock(return_value=good)
        mock_create.return_value = mock_llm
        task = await eval_svc.trigger_evaluation(org.id, sub.id, "submission_review")
        # The outer transaction must still be usable and the eval COMPLETED
        await db.flush()
    assert task.status.value == "completed"
    # The row survives a further roundtrip through the same session
    row = await db.get(EvaluationTask, task.id)
    assert row is not None and row.status.value == "completed"


@pytest.mark.asyncio
async def test_backfill_bound_open_period_accepted_closed_rejected(db):
    """R129[H8/M4]: the manual-ingest past bound is the last CLOSED period's
    end — falling back to the OPEN period's start (not the current calendar
    month) when no closed period exists. Backfill inside the tenant's own
    open (never-invoiced) window must land; anything inside a closed
    (invoiced) window must 422."""
    from datetime import timedelta

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.billing import BillingPeriod
    from app.controlplane.services import billing as billing_svc
    from app.core.security import create_access_token
    from app.main import app
    from app.services.organization import OrgService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"MB {ULID()}",
        slug=f"mb-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=Actor(user_id=user.id, type="platform"),
    )
    now = datetime.now(UTC)
    # Rewrite the auto-created open period to start 40 days ago (a long
    # overdue first period spanning at least one month boundary) and add an
    # older invoiced period before it.
    open_period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    open_period.period_start = now - timedelta(days=40)
    await db.commit()

    token = create_access_token(user.id, user.email, user.role.value)
    hdrs = {"Authorization": f"Bearer {token}"}
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _noop(_):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # 35 days ago: inside the OPEN first period (and always before the
        # current calendar month start — the exact H8 false-reject shape).
        r = await c.post(
            f"/api/v1/orgs/{org.id}/usage-events",
            json={
                "usage_type": "image_generation",
                "quantity": "3",
                "occurred_at": (now - timedelta(days=35)).isoformat(),
                "idempotency_key": f"h8-open-{ULID()}",
            },
            headers=hdrs,
        )
        assert r.status_code == 201, r.text
        # Now record an INVOICED period before the open one — 50 days ago
        # falls inside it → rejected.
        async with AsyncSessionLocal() as s2:
            s2.add(
                BillingPeriod(
                    tenant_id=tenant.id,
                    subscription_id=sub.id,
                    period_start=now - timedelta(days=70),
                    period_end=now - timedelta(days=40),
                    status="invoiced",
                )
            )
            await s2.commit()
        r = await c.post(
            f"/api/v1/orgs/{org.id}/usage-events",
            json={
                "usage_type": "image_generation",
                "quantity": "3",
                "occurred_at": (now - timedelta(days=50)).isoformat(),
                "idempotency_key": f"h8-closed-{ULID()}",
            },
            headers=hdrs,
        )
        assert r.status_code == 422, r.text
        assert "already-invoiced" in r.json()["error"]["message"]


@pytest.mark.asyncio
async def test_seat_sweep_isolates_one_bad_org(db, monkeypatch):
    """R169: one org whose emit_usage raises must NOT abort the whole MONTHLY
    seat sweep (it fires only on the 1st — an unguarded abort loses a full
    month of seat billing platform-wide). The healthy org still gets its
    seat event; the poison org's savepoint rolls back cleanly."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    owner = await _mk_user(db)
    svc = OrgService(db)
    orgs = []
    for _ in range(2):
        o = await svc.create(
            name=f"IsoSweep {ULID()}",
            slug=f"iso-{str(ULID()).lower()}",
            description=None,
            created_by=owner.id,
        )
        s = await _mk_user(db)
        await svc.add_member(o.id, s.id, OrgRole.STUDENT)
        orgs.append(o.id)
    await db.flush()
    month = datetime.now(UTC).strftime("%Y-%m")
    poison_org = orgs[0]

    real_emit = metering.emit_usage

    async def flaky_emit(db_, **kw):
        if kw.get("org_id") == poison_org and kw.get("usage_type") == "active_learner_seat":
            raise RuntimeError("simulated emit failure")
        return await real_emit(db_, **kw)

    monkeypatch.setattr(metering, "emit_usage", flaky_emit)
    # Must NOT raise despite the poison org.
    emitted = await metering.sweep_seats(db, for_month=month)
    await db.flush()
    monkeypatch.undo()

    # The healthy org still got its seat event; the poison org did not.
    for oid in orgs:
        rows = (
            (
                await db.execute(
                    select(UsageEvent).where(
                        UsageEvent.idempotency_key == f"seats:{oid}:{month}"
                    )
                )
            )
            .scalars()
            .all()
        )
        if oid == poison_org:
            assert len(rows) == 0, "poison org's savepoint must have rolled back"
        else:
            assert len(rows) == 1, "healthy org must still be seat-billed"
    assert emitted >= 1



@pytest.mark.asyncio
async def test_storage_sweep_exact_gb_idempotent_and_poison_isolated(db, monkeypatch):
    """R257: sweep_storage was fully untested — exact GB math (bytes/2^30 at
    6dp), idempotent rerun, zero-storage skip, and the R169 poison-org
    SAVEPOINT isolation (one org whose emit raises must not wedge the sweep)."""
    from datetime import timedelta
    from decimal import Decimal

    from app.models.project import ProjectAsset
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    owner = await _mk_user(db)
    svc = OrgService(db)
    org = await svc.create(
        name=f"Stor {ULID()}", slug=f"stor-{str(ULID()).lower()}",
        description=None, created_by=owner.id)
    project = await ProjectService(db).create_project(
        org_id=org.id, title="Storage P", slug=None, description="d",
        instructions="i", difficulty="beginner", max_score=100,
        rubric=[{"criterion": "Q", "max_score": 100}], deadline=None,
        late_deadline=None, late_penalty_pct=0, max_submissions=0,
        skill_ids=None, created_by=owner.id)
    db.add(ProjectAsset(
        org_id=org.id, project_id=project.id, name="ref", description=None,
        file_key=f"k/{ULID()}", file_name="ref.bin", file_size=1073741824,  # 1 GiB
        mime_type="application/octet-stream", uploaded_by=owner.id))
    await db.flush()

    n1 = await metering.sweep_storage(db, org_ids=[org.id])
    assert n1 == 1
    day = datetime.now(UTC).date().isoformat()
    ev = (
        await db.execute(
            select(UsageEvent).where(UsageEvent.idempotency_key == f"storage:{org.id}:{day}")
        )
    ).scalar_one()
    assert ev.usage_type == "storage_gb_day"
    assert Decimal(str(ev.quantity)) == Decimal("1")     # exactly 1 GiB → 1.000000

    n2 = await metering.sweep_storage(db, org_ids=[org.id])  # idempotent rerun
    dup = (
        (await db.execute(
            select(UsageEvent).where(UsageEvent.idempotency_key == f"storage:{org.id}:{day}")
        )).scalars().all()
    )
    assert len(dup) == 1 and n2 == 0

    # R169 poison isolation: an emit_usage that raises for one org must not
    # abort the sweep for the others
    org2 = await svc.create(
        name=f"Stor2 {ULID()}", slug=f"stor2-{str(ULID()).lower()}",
        description=None, created_by=owner.id)
    db.add(ProjectAsset(
        org_id=org2.id, project_id=project.id, name="x", description=None,
        file_key=f"k/{ULID()}", file_name="x.bin", file_size=2147483648,  # 2 GiB
        mime_type="application/octet-stream", uploaded_by=owner.id))
    await db.flush()
    real_emit = metering.emit_usage

    async def poison_emit(db_, **kw):
        if kw.get("org_id") == org.id:                   # first org poisoned
            raise RuntimeError("poison org")
        return await real_emit(db_, **kw)

    monkeypatch.setattr(metering, "emit_usage", poison_emit)
    n3 = await metering.sweep_storage(
        db, for_date=datetime.now(UTC) + timedelta(days=1), org_ids=[org.id, org2.id])
    assert n3 == 1                                       # org2 still swept
    day2 = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()
    ok2 = (
        await db.execute(
            select(UsageEvent).where(UsageEvent.idempotency_key == f"storage:{org2.id}:{day2}")
        )
    ).scalar_one_or_none()
    assert ok2 is not None and Decimal(str(ok2.quantity)) == Decimal("2")


@pytest.mark.asyncio
async def test_adjustment_keyed_retry_semantics(db):
    """R341 (mutation survivors — the keyed-retry arcs R131[10]/R132[F6][15]/
    R133[F8] had no tests): a keyed adjustment retry with the SAME payload is
    an idempotent success (same row back), even when ANOTHER tenant holds the
    same key (per-tenant index scope) and even when the retry's delta differs
    only past the column's 6dp scale; the same key with a DIFFERENT delta is
    a 409; a key already used by a NON-adjustment event is a 409; adjusting a
    voided rating is a 409; a missing original is a 404."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    tenant_b = await _mk_tenant(db, user)
    actor = Actor(user_id=user.id, type="platform")

    def _emit_kw(t, key):
        return dict(tenant_id=t.id, org_id="01JFAKEORGFAKEORGFAKEORGFA",
                    usage_type="image_generation", quantity=10,
                    occurred_at=_now(), source="manual", idempotency_key=key)

    original = await metering.emit_usage(db, **_emit_kw(tenant, f"orig-{ULID()}"))
    adj_key = f"adj-{ULID()}"
    # tenant B holds the SAME key (per-tenant unique index allows it) — the
    # retry lookup must never match B's event
    await metering.emit_usage(db, **_emit_kw(tenant_b, adj_key))

    adj = await metering.ingest_adjustment(
        db, original_event_id=original.id, delta_quantity=-4,
        reason="r341", actor=actor, idempotency_key=adj_key)
    # 1. same key + same delta → idempotent success, SAME row
    again = await metering.ingest_adjustment(
        db, original_event_id=original.id, delta_quantity=-4,
        reason="r341 retry", actor=actor, idempotency_key=adj_key)
    assert again.id == adj.id
    # 2. same at the 6dp column scale (7th-decimal noise) → still idempotent
    again2 = await metering.ingest_adjustment(
        db, original_event_id=original.id, delta_quantity="-4.0000004",
        reason="r341 retry 6dp", actor=actor, idempotency_key=adj_key)
    assert again2.id == adj.id
    # 3. same key, DIFFERENT delta → 409 (Stripe-style key semantics)
    with pytest.raises(AppError) as e409:
        await metering.ingest_adjustment(
            db, original_event_id=original.id, delta_quantity=-5,
            reason="r341 conflict", actor=actor, idempotency_key=adj_key)
    assert e409.value.status_code == 409
    assert "different delta_quantity" in e409.value.message
    # 4. a key already used by a NON-adjustment event → duplicate 409
    with pytest.raises(AppError) as e409b:
        await metering.ingest_adjustment(
            db, original_event_id=original.id, delta_quantity=-1,
            reason="r341 dup", actor=actor,
            idempotency_key=original.idempotency_key)
    assert e409b.value.status_code == 409
    assert "Duplicate adjustment idempotency key" in e409b.value.message
    # 5. missing original → 404
    with pytest.raises(AppError) as e404:
        await metering.ingest_adjustment(
            db, original_event_id=str(ULID()), delta_quantity=-1,
            reason="r341 gone", actor=actor)
    assert e404.value.status_code == 404 and e404.value.code == "USAGE_EVENT_NOT_FOUND"

    # 6. adjusting a VOIDED rating double-corrects → 409 (R130[37]) — fresh
    # original (the mirror gate correctly refuses to void an ADJUSTED event)
    from app.controlplane.services import rating as rating_svc

    orig2 = await metering.emit_usage(db, **_emit_kw(tenant, f"orig2-{ULID()}"))
    rated2 = await rating_svc.rate_event(db, orig2.id)
    await rating_svc.void_rated(db, rated2.id, reason="strike", actor=actor)
    with pytest.raises(AppError) as e409c:
        await metering.ingest_adjustment(
            db, original_event_id=orig2.id, delta_quantity=-2,
            reason="r341 voided", actor=actor)
    assert e409c.value.status_code == 409 and "voided" in e409c.value.message


@pytest.mark.asyncio
async def test_adjustment_open_period_warning_is_tenant_scoped(db, monkeypatch):
    """R341: the no-open-period warning (money that will never be invoiced)
    must key off the ORIGINAL's tenant — tenant A's open period must not
    silence tenant B's warning — and two open periods (live + cancelled subs'
    residue) must not 500 the lookup."""
    from datetime import timedelta

    from app.controlplane.models.billing import BillingPeriod, Subscription
    from app.controlplane.models.plan import PlanVersion, ProductPlan

    user = await _mk_user(db)
    a = await _mk_tenant(db, user)
    b = await _mk_tenant(db, user)
    actor = Actor(user_id=user.id, type="platform")
    now = _now()

    plan = ProductPlan(key=f"r341-{str(ULID()).lower()[:8]}", name="R341")
    db.add(plan)
    await db.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, status="active",
                     entitlements={}, activated_at=now)
    db.add(pv)
    await db.flush()

    def _sub(status):
        return Subscription(
            tenant_id=a.id, plan_version_id=pv.id, status=status,
            currency="USD", interval="month", seat_quantity=0,
            current_period_start=now - timedelta(days=5),
            current_period_end=now + timedelta(days=25),
            provider="manual", created_by=user.id)

    live, dead = _sub("active"), _sub("cancelled")
    db.add_all([live, dead])
    await db.flush()
    # TWO open periods for tenant A (live sub + a cancelled sub's residue)
    db.add_all([
        BillingPeriod(tenant_id=a.id, subscription_id=live.id, status="open",
                      period_start=now - timedelta(days=5),
                      period_end=now + timedelta(days=25)),
        BillingPeriod(tenant_id=a.id, subscription_id=dead.id, status="open",
                      period_start=now - timedelta(days=35),
                      period_end=now - timedelta(days=5)),
    ])
    await db.flush()

    warnings: list = []
    real_warning = metering.log.warning
    monkeypatch.setattr(metering.log, "warning",
                        lambda *aa, **kw: warnings.append((aa, kw)) or real_warning(*aa, **kw))

    def _kw(t):
        return dict(tenant_id=t.id, org_id="01JFAKEORGFAKEORGFAKEORGFA",
                    usage_type="image_generation", quantity=5,
                    occurred_at=now, source="manual",
                    idempotency_key=f"w-{ULID()}")

    # A HAS open periods (two of them) → no warning, no 500
    orig_a = await metering.emit_usage(db, **_kw(a))
    await metering.ingest_adjustment(db, original_event_id=orig_a.id,
                                     delta_quantity=-1, reason="a", actor=actor)
    assert not any(x[0] and x[0][0] == "cp_adjustment_no_open_period" for x in warnings)

    # B has NONE → warning fires (A's period must not silence it)
    orig_b = await metering.emit_usage(db, **_kw(b))
    await metering.ingest_adjustment(db, original_event_id=orig_b.id,
                                     delta_quantity=-1, reason="b", actor=actor)
    assert any(x[0] and x[0][0] == "cp_adjustment_no_open_period" for x in warnings)


@pytest.mark.asyncio
async def test_flush_boundaries_zero_buckets_and_org_attribution(db):
    """R341 (mutation survivors): the hourly flush's exact edges —
    (1) the CURRENT hour bucket is never flushed mid-accumulation;
    (2) a ZERO-count bucket emits nothing but still counts as landed (an
        ancient zero bucket is deleted, not kept forever);
    (3) a bucket exactly AT the 25h delete-cutoff is KEPT (strict <);
    (4) org attribution resolves an org of THIS tenant (a two-org tenant
        flushes cleanly — limit(1)). The scan_iter count=500 mutant is a
    performance hint with no semantics — documented equivalent."""
    from datetime import timedelta

    from app.controlplane.services.metering import flush_api_request_counters
    from app.models.organization import Organization

    user = await _mk_user(db)
    other_tenant = await _mk_tenant(db, user)   # decoy first (scan-order bait)
    other_org = Organization(name=f"D {ULID()}", slug=f"do-{str(ULID()).lower()}",
                             tenant_id=other_tenant.id, created_by=user.id)
    db.add(other_org)
    tenant = await _mk_tenant(db, user)
    org1 = Organization(name=f"A {ULID()}", slug=f"oa-{str(ULID()).lower()}",
                        tenant_id=tenant.id, created_by=user.id)
    org2 = Organization(name=f"B {ULID()}", slug=f"ob-{str(ULID()).lower()}",
                        tenant_id=tenant.id, created_by=user.id)
    db.add_all([org1, org2])
    await db.flush()
    await db.commit()

    r = await _fresh_redis()
    now = datetime.now(UTC)
    cur_bucket = now.strftime("%Y%m%d%H")
    cutoff_bucket = (now - timedelta(hours=25)).strftime("%Y%m%d%H")
    zero_bucket = (now - timedelta(hours=30)).strftime("%Y%m%d%H")
    recent_bucket = (now - timedelta(hours=2)).strftime("%Y%m%d%H")
    keys = {
        "cur": f"cp:apireq:{tenant.id}:{cur_bucket}",
        "cutoff": f"cp:apireq:{tenant.id}:{cutoff_bucket}",
        "zero": f"cp:apireq:{tenant.id}:{zero_bucket}",
        "recent": f"cp:apireq:{tenant.id}:{recent_bucket}",
    }
    old26_bucket = (now - timedelta(hours=26)).strftime("%Y%m%d%H")
    keys["old26"] = f"cp:apireq:{tenant.id}:{old26_bucket}"
    # clear any residue from other tests so the emitted count is exact
    async for stale in r.scan_iter(match="cp:apireq:*", count=500):
        await r.delete(stale)
    await r.set(keys["cur"], 11, ex=90_000)
    await r.set(keys["cutoff"], 13, ex=90_000)
    await r.set(keys["zero"], 0, ex=90_000)
    await r.set(keys["recent"], 17, ex=90_000)
    await r.set(keys["old26"], 19, ex=90_000)
    try:
        emitted = await flush_api_request_counters(db)
        # exact landing count: cutoff-13, recent-17, old26-19 (zero + current
        # hour emit nothing) — each counted ONCE
        assert emitted == 3
        # a bucket STRICTLY older than the 25h cutoff is deleted after landing
        assert await r.get(keys["old26"]) is None
        # (1) current hour untouched — not emitted, not deleted
        assert await r.get(keys["cur"]) is not None
        # (3) exactly-at-cutoff bucket KEPT (delete is strictly older-than)
        assert await r.get(keys["cutoff"]) is not None
        # (2) ancient zero bucket deleted without emitting an event
        assert await r.get(keys["zero"]) is None
        events = (
            await db.execute(
                select(UsageEvent).where(
                    UsageEvent.tenant_id == tenant.id,
                    UsageEvent.usage_type == "api_request"))
        ).scalars().all()
        quantities = sorted(int(e.quantity) for e in events)
        assert 11 not in quantities          # current hour never landed
        assert 0 not in quantities           # zero bucket emitted nothing
        assert 13 in quantities and 17 in quantities and 19 in quantities
        # (4) attribution org belongs to THIS tenant (two orgs, no 500)
        assert {e.org_id for e in events} <= {org1.id, org2.id}
    finally:
        await r.delete(*keys.values())


@pytest.mark.asyncio
async def test_storage_sweep_combines_sources_and_skips_zero(db):
    """R342 (mutation survivors): per-org storage totals must (1) attribute
    submission-item bytes through the item→submission JOIN (a flipped join
    smears every other submission's bytes into the org), (2) SUM item + asset
    bytes for the same org, and (3) skip zero-byte orgs entirely (no
    0-quantity events). The 5000-chunk mutants are IN-list sizing —
    documented equivalent below that cardinality."""
    from decimal import Decimal

    from app.models.project import (
        DeliverableType,
        ItemType,
        ProjectAsset,
        ProjectDeliverable,
        Submission,
        SubmissionItem,
        SubmissionStatus,
    )
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    owner = await _mk_user(db)
    svc = OrgService(db)

    async def _org_with_project(tag):
        org = await svc.create(name=f"S{tag} {ULID()}",
                               slug=f"s{tag}-{str(ULID()).lower()}",
                               description=None, created_by=owner.id)
        project = await ProjectService(db).create_project(
            org_id=org.id, title=f"P{tag}", slug=None, description="d",
            instructions="i", difficulty="beginner", max_score=100,
            rubric=[{"criterion": "Q", "max_score": 100}], deadline=None,
            late_deadline=None, late_penalty_pct=0, max_submissions=0,
            skill_ids=None, created_by=owner.id)
        return org, project

    async def _item(org, project, size):
        sub = Submission(org_id=org.id, project_id=project.id, user_id=owner.id,
                         version=1, status=SubmissionStatus.SUBMITTED,
                         submitted_at=datetime.now(UTC))
        db.add(sub)
        await db.flush()
        deliverable = ProjectDeliverable(project_id=project.id, name="D",
                                         type=DeliverableType.TEXT)
        db.add(deliverable)
        await db.flush()
        db.add(SubmissionItem(submission_id=sub.id, deliverable_id=deliverable.id,
                              type=ItemType.TEXT, content="x", file_size=size,
                              uploaded_by=owner.id))
        await db.flush()

    gib = 1073741824
    # org D: asset 1 GiB + submission item 0.5 GiB → 1.5 GB event
    org_d, proj_d = await _org_with_project("d")
    db.add(ProjectAsset(org_id=org_d.id, project_id=proj_d.id, name="a",
                        description=None, file_key=f"k/{ULID()}", file_name="a.bin",
                        file_size=gib, mime_type="application/octet-stream",
                        uploaded_by=owner.id))
    await _item(org_d, proj_d, gib // 2)
    # org E: its own item 0.25 GiB (join-flip bait: with != it would absorb D's)
    org_e, proj_e = await _org_with_project("e")
    await _item(org_e, proj_e, gib // 4)
    # org F: a zero-byte asset → NO event
    org_f, proj_f = await _org_with_project("f")
    db.add(ProjectAsset(org_id=org_f.id, project_id=proj_f.id, name="z",
                        description=None, file_key=f"k/{ULID()}", file_name="z.bin",
                        file_size=0, mime_type="application/octet-stream",
                        uploaded_by=owner.id))
    await db.flush()

    emitted = await metering.sweep_storage(
        db, org_ids=[org_d.id, org_e.id, org_f.id])
    assert emitted == 2                      # D and E; F (zero bytes) skipped
    day = datetime.now(UTC).date().isoformat()

    async def _qty(org):
        ev = (
            await db.execute(
                select(UsageEvent).where(
                    UsageEvent.idempotency_key == f"storage:{org.id}:{day}"))
        ).scalar_one_or_none()
        return None if ev is None else Decimal(str(ev.quantity))

    assert await _qty(org_d) == Decimal("1.5")     # asset + item summed
    assert await _qty(org_e) == Decimal("0.25")    # only its own item
    assert await _qty(org_f) is None               # zero bytes → no event

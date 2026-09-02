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
    n1 = await metering.sweep_seats(db, for_month=month)
    assert n1 >= 1
    await metering.sweep_seats(db, for_month=month)
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

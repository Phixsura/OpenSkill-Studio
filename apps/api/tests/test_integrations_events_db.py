"""Event mesh P2 DB tests — emit/fan-out/dispatch/retry/exhaust/auto-disable/
replay/signing, driven inline through the outbox worker (no Redis)."""

import base64
import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.controlplane.worker import process_outbox_once
from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.facade import emit_event
from app.integrations.models import (
    MAX_ATTEMPTS,
    RETRY_OFFSETS_S,
    DeliveryAttempt,
    EventDelivery,
    IntegrationEvent,
)
from app.integrations.services.events import (
    build_delivery_headers,
    event_matches,
    replay_delivery,
)
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus
from app.models.webhook import WebhookSubscription

INTG_TOPICS = ["intg.event.created", "intg.delivery.attempt"]


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _org(db):
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    u = User(
        email=f"ev-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Ev",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=u.id, type="platform"),
        owner_user_id=u.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=u.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE))
    await db.flush()
    return org


async def _sub(db, org, events=None, url="https://hooks.example.com/sink"):
    sub = WebhookSubscription(
        org_id=org.id,
        url=url,
        events=events or ["com.openskill.project.*"],
        secret="a" * 64,
        active=True,
    )
    db.add(sub)
    await db.flush()
    return sub


class _FakeEgress:
    """Swap for EgressClient: records calls, returns scripted status codes."""

    def __init__(self, codes):
        self.codes = list(codes)
        self.calls = []

    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        self.calls.append({"method": method, "url": url, "headers": headers, "body": content})
        code = self.codes.pop(0) if self.codes else 200
        if code == -1:
            raise httpx.ConnectTimeout("boom")
        return httpx.Response(code, request=httpx.Request(method, url))


@pytest.fixture
def egress(monkeypatch):
    fake = _FakeEgress([200])

    from app.integrations.services import events as svc

    monkeypatch.setattr(svc, "EgressClient", lambda: fake)
    return fake


async def _drain(db, rounds=10):
    """Drive the outbox until quiet (due messages only)."""
    total = 0
    for _ in range(rounds):
        n = await process_outbox_once(db, topics=INTG_TOPICS)
        total += n
        if n == 0:
            break
    return total


# ── matching ──


def test_event_matches_rules():
    t = "com.openskill.project.approved.v1"
    assert event_matches([t], t)
    assert event_matches(["com.openskill.project.*"], t)
    assert not event_matches(["com.openskill.skill.*"], t)
    # internal events: exact only — wildcards never route them
    it = "com.openskill.integration.delivery.exhausted.v1"
    assert not event_matches(["com.openskill.*"], it)
    assert not event_matches(["com.openskill.integration.*"], it)
    assert event_matches([it], it)
    assert not event_matches([42, None], t)  # junk-tolerant


# ── emit + fan-out + happy-path delivery ──


@pytest.mark.asyncio
async def test_emit_fanout_deliver_success(db, egress):
    org = await _org(db)
    sub = await _sub(db, org)
    other = await _sub(db, org, events=["com.openskill.skill.*"])  # no match
    event = await emit_event(
        db, org.id, "project.approved", subject="proj-1", data={"project_id": "p1"}
    )
    await db.commit()
    await _drain(db)

    deliveries = (
        (await db.execute(select(EventDelivery).where(EventDelivery.event_id == event.id)))
        .scalars()
        .all()
    )
    assert len(deliveries) == 1
    d = deliveries[0]
    assert d.subscription_id == sub.id
    assert d.status == "succeeded"
    assert d.attempt_count == 1
    assert other.id not in {x.subscription_id for x in deliveries}

    # Wire check: CloudEvents body + Standard Webhooks headers.
    call = egress.calls[0]
    body = json.loads(call["body"])
    assert body["specversion"] == "1.0"
    assert body["id"] == event.id
    assert body["type"] == "com.openskill.project.approved.v1"
    assert body["data"] == {"project_id": "p1"}
    h = call["headers"]
    assert h["webhook-id"] == event.id
    sig = h["webhook-signature"]
    signed = f"{event.id}.{h['webhook-timestamp']}.".encode() + call["body"]
    expect = base64.b64encode(hmac.new(sub.secret.encode(), signed, hashlib.sha256).digest())
    assert sig == "v1," + expect.decode()


@pytest.mark.asyncio
async def test_fanout_idempotent_on_outbox_redelivery(db, egress):
    from app.integrations.services.events import handle_event_created

    org = await _org(db)
    await _sub(db, org)
    event = await emit_event(db, org.id, "project.approved", data={})
    await db.flush()
    await handle_event_created(db, {"event_id": event.id})
    await handle_event_created(db, {"event_id": event.id})  # redelivery
    count = (
        await db.execute(select(EventDelivery).where(EventDelivery.event_id == event.id))
    ).scalars().all()
    assert len(count) == 1


# ── retry ladder + exhaustion ──


@pytest.mark.asyncio
async def test_failure_schedules_ladder_and_exhausts(db, monkeypatch):
    from app.controlplane.models.outbox import OutboxMessage
    from app.integrations.services import events as svc

    fake = _FakeEgress([500] * MAX_ATTEMPTS)
    monkeypatch.setattr(svc, "EgressClient", lambda: fake)

    org = await _org(db)
    sub = await _sub(db, org)
    event = await emit_event(db, org.id, "project.approved", data={})
    await db.commit()

    # Attempt 1 runs now and fails -> schedules attempt 2 at +5s (not due).
    await _drain(db)
    d = (
        await db.execute(select(EventDelivery).where(EventDelivery.event_id == event.id))
    ).scalar_one()
    assert d.status == "pending"
    assert d.attempt_count == 1
    msg = (
        await db.execute(
            select(OutboxMessage)
            .where(OutboxMessage.topic == "intg.delivery.attempt", OutboxMessage.status == "pending")
            .order_by(OutboxMessage.created_at.desc())
        )
    ).scalars().first()
    assert msg is not None

    # Force each scheduled retry due NOW and drain, until exhaustion.
    for i in range(2, MAX_ATTEMPTS + 1):
        msg.available_at = datetime.now(UTC) - timedelta(seconds=1)
        await db.commit()
        await _drain(db)
        await db.refresh(d)
        if i < MAX_ATTEMPTS:
            assert d.attempt_count == i
            assert d.status == "pending"
            # ladder delay for the NEXT attempt matches the spec table
            expected = RETRY_OFFSETS_S[i - 1]
            delta = (d.next_attempt_at - datetime.now(UTC)).total_seconds()
            assert expected - 60 < delta <= expected + 5
            msg = (
                await db.execute(
                    select(OutboxMessage)
                    .where(
                        OutboxMessage.topic == "intg.delivery.attempt",
                        OutboxMessage.status == "pending",
                    )
                    .order_by(OutboxMessage.created_at.desc())
                )
            ).scalars().first()
        else:
            assert d.status == "exhausted"

    attempts = (
        await db.execute(select(DeliveryAttempt).where(DeliveryAttempt.delivery_id == d.id))
    ).scalars().all()
    assert len(attempts) == MAX_ATTEMPTS
    assert all(a.error == "http_500" for a in attempts)

    # Exhaustion emitted the alertable internal event.
    exhausted_ev = (
        await db.execute(
            select(IntegrationEvent).where(
                IntegrationEvent.org_id == org.id,
                IntegrationEvent.type
                == "com.openskill.integration.delivery.exhausted.v1",
            )
        )
    ).scalars().all()
    assert len(exhausted_ev) == 1
    assert exhausted_ev[0].data["subscription_id"] == sub.id


# ── auto-disable (5-day consistent failure) ──


@pytest.mark.asyncio
async def test_auto_disable_after_five_days_of_failure(db, monkeypatch):
    from app.integrations.services import events as svc

    org = await _org(db)
    sub = await _sub(db, org)
    event = await emit_event(db, org.id, "project.approved", data={})
    await db.flush()
    # Backdate an exhausted delivery to 6 days ago; no success since.
    old = EventDelivery(
        event_id=event.id,
        subscription_id=sub.id,
        status="exhausted",
        attempt_count=MAX_ATTEMPTS,
        created_at=datetime.now(UTC) - timedelta(days=6),
    )
    db.add(old)
    await db.flush()
    await svc._maybe_auto_disable(db, sub, datetime.now(UTC))
    assert sub.active is False

    # With a RECENT success the same evidence does NOT disable.
    sub2 = await _sub(db, org, url="https://hooks.example.com/sink2")
    ok = EventDelivery(
        event_id=event.id,
        subscription_id=sub2.id,
        status="succeeded",
        attempt_count=1,
        created_at=datetime.now(UTC) - timedelta(days=1),
    )
    bad = EventDelivery(
        event_id=event.id,
        subscription_id=sub2.id,
        status="exhausted",
        attempt_count=MAX_ATTEMPTS,
        created_at=datetime.now(UTC) - timedelta(days=6),
        replay_of="x",  # second row for same (event,sub): mark as replay
    )
    db.add_all([ok, bad])
    await db.flush()
    await svc._maybe_auto_disable(db, sub2, datetime.now(UTC))
    assert sub2.active is True


# ── replay ──


@pytest.mark.asyncio
async def test_replay_clones_and_dispatches(db, egress):
    org = await _org(db)
    await _sub(db, org)
    event = await emit_event(db, org.id, "project.approved", data={})
    await db.commit()
    await _drain(db)
    d = (
        await db.execute(select(EventDelivery).where(EventDelivery.event_id == event.id))
    ).scalar_one()
    assert d.status == "succeeded"

    clone = await replay_delivery(db, org.id, d.id)
    assert clone.replay_of == d.id
    await db.commit()
    await _drain(db)
    await db.refresh(clone)
    assert clone.status == "succeeded"
    # Replay reuses the same webhook-id (= event id): receiver dedup works.
    assert egress.calls[-1]["headers"]["webhook-id"] == event.id

    # In-flight second replay is refused; cross-tenant is a uniform 404.
    clone2 = await replay_delivery(db, org.id, d.id)
    clone2.status = "pending"
    with pytest.raises(AppError) as e:
        await replay_delivery(db, org.id, d.id)
    assert e.value.code == "DELIVERY_NOT_REPLAYABLE"
    other_org = await _org(db)
    with pytest.raises(AppError) as e2:
        await replay_delivery(db, other_org.id, d.id)
    assert e2.value.status_code == 404


# ── secret rotation co-signing ──


def test_rotated_secret_co_signs_within_window():
    sub = WebhookSubscription(
        org_id="o",
        url="https://x.example.com/h",
        events=[],
        secret="new" * 10,
        secret_prev="old" * 10,
        secret_rotated_at=datetime.now(UTC) - timedelta(days=2),
        active=True,
    )
    h = build_delivery_headers(sub, "evt_1", b"{}", datetime.now(UTC))
    sigs = h["webhook-signature"].split(" ")
    assert len(sigs) == 2 and all(s.startswith("v1,") for s in sigs)
    # Outside the 7-day window the old secret stops signing.
    sub.secret_rotated_at = datetime.now(UTC) - timedelta(days=8)
    h2 = build_delivery_headers(sub, "evt_1", b"{}", datetime.now(UTC))
    assert len(h2["webhook-signature"].split(" ")) == 1


# ── inactive subscription cancels, event data cap ──


@pytest.mark.asyncio
async def test_inactive_subscription_cancels_delivery(db, egress):
    from app.integrations.services.events import handle_delivery_attempt

    org = await _org(db)
    sub = await _sub(db, org)
    event = await emit_event(db, org.id, "project.approved", data={})
    await db.flush()
    d = EventDelivery(event_id=event.id, subscription_id=sub.id, status="pending")
    db.add(d)
    await db.flush()
    sub.active = False
    await handle_delivery_attempt(db, {"delivery_id": d.id})
    assert d.status == "cancelled"
    assert egress.calls == []


@pytest.mark.asyncio
async def test_event_data_size_cap(db):
    org = await _org(db)
    with pytest.raises(AppError) as e:
        await emit_event(db, org.id, "project.approved", data={"blob": "x" * 70_000})
    assert e.value.code == "EVENT_DATA_TOO_LARGE"


# ── R7 defect #7 pin: mesh patterns subscribable through the real API ──


@pytest.mark.asyncio
async def test_subscription_accepts_mesh_patterns(db):
    from app.exceptions import AppError
    from app.services.webhook import WebhookService

    org = await _org(db)
    svc = WebhookService(db)
    sub = await svc.create(
        org.id,
        "https://hooks.example.com/mesh",
        ["com.openskill.project.*", "com.openskill.credential.issued.v1"],
    )
    assert sub.id
    with pytest.raises(AppError) as e:
        await svc.create(
            org.id, "https://hooks.example.com/x", ["com.openskill.UPPER.*"]
        )
    assert e.value.code == "INVALID_EVENT"
    with pytest.raises(AppError):
        await svc.create(org.id, "https://hooks.example.com/x", ["totally.unknown"])

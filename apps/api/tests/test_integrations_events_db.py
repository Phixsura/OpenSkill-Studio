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
        return httpx.Response(
            code,
            content=(b"" if code < 400 else b"upstream error \x01detail\x02 " + b"x" * 600),
            request=httpx.Request(method, url),
        )


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

    # Wire check: CloudEvents body + Standard Webhooks headers. Pick OUR
    # call by webhook-id — stray pending outbox rows from an earlier aborted
    # run can drain first and occupy calls[0].
    call = next(c for c in egress.calls if c["headers"].get("webhook-id") == event.id)
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

    # Mutating the event row after first dispatch must NOT change the resent
    # bytes — retries resend the ARCHIVE, not a re-render.
    d.status = "pending"
    event.data = {"k": "MUTATED"}
    await db.commit()
    from app.integrations.services.events import handle_delivery_attempt

    await handle_delivery_attempt(db, {"delivery_id": d.id})
    await db.commit()
    wire2 = [c for c in egress.calls if c["headers"].get("webhook-id") == event.id][-1]
    assert wire2["body"] == d.request_body.encode()
    assert b"MUTATED" not in wire2["body"]

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


# ── R14: rotation keeps the old secret co-signing (one behavior everywhere) ──


@pytest.mark.asyncio
async def test_legacy_rotate_cosigns_then_immediate_stops(db):
    from app.integrations.services.events import build_delivery_headers
    from app.services.webhook import WebhookService

    org = await _org(db)
    sub = await _sub(db, org)
    old_secret = sub.secret
    svc = WebhookService(db)
    await svc.rotate_secret(sub.id, org.id)
    assert sub.secret != old_secret
    assert sub.secret_prev == old_secret  # zero-downtime co-sign window
    h = build_delivery_headers(sub, "evt", b"{}", datetime.now(UTC))
    assert len(h["webhook-signature"].split(" ")) == 2
    # Leaked-secret path: immediate rotation drops the old key NOW.
    await svc.rotate_secret(sub.id, org.id, immediate=True)
    assert sub.secret_prev is None
    h2 = build_delivery_headers(sub, "evt", b"{}", datetime.now(UTC))
    assert len(h2["webhook-signature"].split(" ")) == 1


def test_event_matches_internal_wildcard_protection():
    """R28 mutation probe: fabric-internal events (integration.*) must match
    on EXACT name only — a '.*' wildcard subscription must never route
    delivery.exhausted notices back into the failing endpoint (feedback
    loop). Also: matching is case-SENSITIVE."""
    from app.integrations.services.events import event_matches

    exhausted = "com.openskill.integration.delivery.exhausted"
    assert not event_matches(["com.openskill.integration.*"], exhausted)
    assert not event_matches(["com.openskill.*"], exhausted)
    assert event_matches([exhausted], exhausted)  # exact still works
    # Normal events: wildcard and exact both match; case matters.
    t = "com.openskill.project.approved.v1"
    assert event_matches(["com.openskill.project.*"], t)
    assert event_matches([t], t)
    assert not event_matches([t.upper()], t)
    assert not event_matches(["com.openskill.proj.*"], t.replace("project", "proj2"))
    # Junk patterns never match, never crash.
    assert not event_matches([None, 42, {}, ""], t)


# ── R44: retention sweep ──


@pytest.mark.asyncio
async def test_retention_sweep_ages_out_terminal_data_only(db):
    from datetime import timedelta as _td

    from app.integrations.services.events import sweep_retention
    from app.models.webhook import WebhookSubscription

    org = await _org(db)
    sub = await _sub(db, org)
    old_time = datetime.now(UTC) - _td(days=200)
    mid_time = datetime.now(UTC) - _td(days=100)

    ev_old = IntegrationEvent(org_id=org.id, type="com.openskill.project.approved.v1",
                              source="/t", subject="old", time=old_time)
    ev_new = IntegrationEvent(org_id=org.id, type="com.openskill.project.approved.v1",
                              source="/t", subject="new")
    db.add_all([ev_old, ev_new])
    await db.flush()
    d_term = EventDelivery(event_id=ev_new.id, subscription_id=sub.id,
                           status="succeeded", attempt_count=1, created_at=mid_time)
    d_pend = EventDelivery(event_id=ev_new.id, subscription_id=sub.id,
                           status="pending", attempt_count=0, created_at=mid_time,
                           replay_of="X")  # dodge the partial-unique original index
    db.add_all([d_term, d_pend])
    await db.flush()
    ids = {"ev_old": ev_old.id, "ev_new": ev_new.id,
           "d_term": d_term.id, "d_pend": d_pend.id}
    await db.commit()

    # A RECENT terminal delivery must survive (age cutoff, not status alone).
    d_recent = EventDelivery(event_id=ev_new.id, subscription_id=sub.id,
                             status="succeeded", attempt_count=1, replay_of="Y")
    db.add(d_recent)
    await db.flush()
    ids["d_recent"] = d_recent.id
    await db.commit()

    # Batch loop drains PAST one batch (kill the one-batch-only mutant).
    import app.integrations.services.events as _ev_mod

    monkeypatch = None
    try:
        from _pytest.monkeypatch import MonkeyPatch

        monkeypatch = MonkeyPatch()
        monkeypatch.setattr(_ev_mod, "_RETENTION_BATCH", 1)
        counts = await sweep_retention(db)
    finally:
        if monkeypatch:
            monkeypatch.undo()
    assert counts["deliveries"] >= 1 and counts["events"] >= 1
    assert await db.get(EventDelivery, ids["d_recent"]) is not None

    assert await db.get(IntegrationEvent, ids["ev_old"]) is None
    assert await db.get(IntegrationEvent, ids["ev_new"]) is not None
    assert await db.get(EventDelivery, ids["d_term"]) is None
    # A delivery still pending NEVER ages out, whatever its age.
    assert await db.get(EventDelivery, ids["d_pend"]) is not None
    # tidy: cancel the pending row so later sweeps may reclaim it.
    (await db.get(EventDelivery, ids["d_pend"])).status = "cancelled"
    await db.commit()
    assert sub is not None and WebhookSubscription is not None


@pytest.mark.asyncio
async def test_subscription_stats_grouped_and_org_scoped(db, egress):
    from app.integrations.api.events import subscription_stats

    org = await _org(db)
    other = await _org(db)
    sub = await _sub(db, org)
    foreign_sub = await _sub(db, other)
    ev = await emit_event(db, org.id, "project.approved", subject="st-1", data={})
    ev2 = await emit_event(db, other.id, "project.approved", subject="st-2", data={})
    await db.commit()
    await _drain(db)

    # The org owner sees only its own subscription's counts.
    owner = (
        await db.execute(
            select(OrgMember).where(OrgMember.org_id == org.id)
        )
    ).scalars().first()
    from app.models.user import User as _User

    user = await db.get(_User, owner.user_id)
    out = await subscription_stats(org.id, db=db, user=user)
    stats = out["data"]
    assert sub.id in stats and stats[sub.id].get("succeeded", 0) >= 1
    assert foreign_sub.id not in stats
    assert ev.id != ev2.id


@pytest.mark.asyncio
async def test_events_api_org_scoping_and_filters(db, egress):
    """R47 API-layer killers: list_events org filter + type_prefix, deliveries
    org filter, delivery-detail uniform 404 cross-org."""
    from app.exceptions import AppError
    from app.integrations.api.events import get_delivery, list_deliveries, list_events
    from app.models.user import User as _User

    org = await _org(db)
    other = await _org(db)
    sub = await _sub(db, org)
    await _sub(db, other)  # foreign deliveries must exist to prove the filter
    ev = await emit_event(db, org.id, "project.approved", subject="api-1", data={})
    await emit_event(db, org.id, "skill.completed", subject="api-2", data={})
    foreign = await emit_event(db, other.id, "project.approved", subject="FOREIGN", data={})
    await db.commit()
    await _drain(db)

    owner_row = (
        await db.execute(select(OrgMember).where(OrgMember.org_id == org.id))
    ).scalars().first()
    user = await db.get(_User, owner_row.user_id)

    out = await list_events(org.id, type_prefix=None, limit=50, db=db, user=user)
    subjects = {e.subject for e in out["data"]}
    assert "api-1" in subjects and "FOREIGN" not in subjects

    out2 = await list_events(
        org.id, type_prefix="com.openskill.skill.", limit=50, db=db, user=user
    )
    assert {e.subject for e in out2["data"]} == {"api-2"}

    dels = await list_deliveries(
        org.id, status=None, subscription_id=None, limit=50, db=db, user=user
    )
    assert all(d.event_id != foreign.id for d in dels["data"])
    assert any(d.event_id == ev.id for d in dels["data"])

    # Cross-org delivery detail: uniform 404.
    mine = next(d for d in dels["data"] if d.event_id == ev.id)
    other_owner_row = (
        await db.execute(select(OrgMember).where(OrgMember.org_id == other.id))
    ).scalars().first()
    other_user = await db.get(_User, other_owner_row.user_id)
    with pytest.raises(AppError) as exc:
        await get_delivery(other.id, mine.id, db=db, user=other_user)
    assert exc.value.status_code == 404
    assert sub is not None


@pytest.mark.asyncio
async def test_attempt_response_snippet_captured_sanitized_and_capped(db, egress):
    """R60: failed attempts keep a sanitized 500-char response snippet;
    successful attempts never retain the body."""
    from app.integrations.models import DeliveryAttempt

    org = await _org(db)
    await _sub(db, org)
    egress.codes = [500, 200]
    ev = await emit_event(db, org.id, "project.approved", subject="sn-1", data={})
    await db.commit()
    await _drain(db)
    # drive the retry (scheduled later) — force due now
    from app.controlplane.models.outbox import OutboxMessage

    rows = (
        await db.execute(select(OutboxMessage).where(OutboxMessage.status == "pending"))
    ).scalars().all()
    for r in rows:
        r.available_at = datetime.now(UTC)
    await db.commit()
    await _drain(db)

    attempts = (
        (
            await db.execute(
                select(DeliveryAttempt)
                .join(EventDelivery, EventDelivery.id == DeliveryAttempt.delivery_id)
                .where(EventDelivery.event_id == ev.id)
                .order_by(DeliveryAttempt.attempted_at)
            )
        )
        .scalars()
        .all()
    )
    assert len(attempts) == 2
    failed, ok = attempts[0], attempts[-1]
    assert failed.status_code == 500
    assert failed.response_snippet is not None
    assert len(failed.response_snippet) <= 500
    assert "\x01" not in failed.response_snippet  # control chars stripped
    assert failed.response_snippet.startswith("upstream error")
    assert ok.status_code == 200 and ok.response_snippet is None


@pytest.mark.asyncio
async def test_webhook_update_in_place(db):
    """R77: url/events edit + re-enable without secret rotation; blocked
    URLs and junk events refused; cross-org uniform 404."""
    from app.services.webhook import WebhookService

    org = await _org(db)
    other = await _org(db)
    svc = WebhookService(db)
    sub = await _sub(db, org)
    old_secret = sub.secret

    out = await svc.update(
        sub.id, org.id,
        url="https://new-receiver.example.com/hook",
        events=["com.openskill.skill.*"],
        actor_user_id=None,
    )
    assert out.url == "https://new-receiver.example.com/hook"
    assert out.events == ["com.openskill.skill.*"]
    assert out.secret == old_secret  # edit never rotates

    # Re-enable after auto-disable.
    sub.active = False
    await db.flush()
    out2 = await svc.update(sub.id, org.id, active=True)
    assert out2.active is True

    from app.exceptions import AppError

    with pytest.raises(AppError) as e1:
        await svc.update(sub.id, org.id, url="http://169.254.169.254/x")
    assert e1.value.code == "WEBHOOK_URL_BLOCKED"
    with pytest.raises(AppError) as e2:
        await svc.update(sub.id, org.id, events=["totally.unknown"])
    assert e2.value.code == "INVALID_EVENT"
    with pytest.raises(AppError) as e3:
        await svc.update(sub.id, other.id, active=False)
    assert e3.value.status_code == 404


@pytest.mark.asyncio
async def test_event_catalog_lists_legacy_canonical_and_internals(db):
    from app.integrations.api.events import event_catalog
    from app.models.user import User as _User

    org = await _org(db)
    owner_row = (
        await db.execute(select(OrgMember).where(OrgMember.org_id == org.id))
    ).scalars().first()
    user = await db.get(_User, owner_row.user_id)
    out = await event_catalog(org.id, db=db, user=user)
    data = out["data"]
    assert "credential.issued" in data["legacy"]
    assert "com.openskill.project.approved.v1" in data["canonical"]
    # Legacy->canonical rename honored (ecosystem.change -> change_verified).
    assert "com.openskill.ecosystem.change_verified.v1" in data["canonical"]
    assert "com.openskill.project.*" in data["wildcards"]
    assert "com.openskill.integration.delivery.exhausted.v1" in data["internal"]
    # Every advertised pattern is actually accepted by the create validator.
    from app.services.webhook import _MESH_PATTERN_RE, VALID_EVENT_TYPES

    for t in data["canonical"] + data["wildcards"] + list(data["internal"]):
        assert _MESH_PATTERN_RE.fullmatch(t) or t in VALID_EVENT_TYPES, t
    assert "com.openskill.org.import.committed.v1" in data["canonical"]  # R143

    # R146 inverse self-consistency: every emit_event CALL SITE in app code
    # uses a type the catalog advertises — a new emission cannot silently
    # ship undiscoverable.
    import pathlib
    import re as _re

    emit_re = _re.compile(r"""emit_event\(\s*[^,]+,\s*[^,]+,\s*["']([a-z0-9_.]+)["']""")
    emitted: set[str] = set()
    for f in pathlib.Path("app").rglob("*.py"):
        emitted |= set(emit_re.findall(f.read_text()))
    assert emitted, "emit_event scan found nothing — regex drifted"
    advertised = set(data["canonical"]) | set(data["internal"])
    for name in emitted:
        assert f"com.openskill.{name}.v1" in advertised, f"{name} emitted but not cataloged"


@pytest.mark.asyncio
async def test_payload_archive_byte_stable_and_replay_inherits(db, egress):
    """R94: first dispatch archives the exact signed bytes; the wire body
    equals the archive; a replay clone inherits it; the payload endpoint
    serves it (uniform 404 cross-org)."""
    from app.integrations.api.events import delivery_payload
    from app.integrations.services.events import replay_delivery
    from app.models.user import User as _User

    org = await _org(db)
    await _sub(db, org)
    ev = await emit_event(db, org.id, "project.approved", subject="ar-1", data={"k": 1})
    await db.commit()
    await _drain(db)
    d = (
        await db.execute(
            select(EventDelivery).where(EventDelivery.event_id == ev.id)
        )
    ).scalars().first()
    assert d.request_body is not None
    wire = next(c for c in egress.calls if c["headers"].get("webhook-id") == ev.id)
    assert wire["body"] == d.request_body.encode()  # byte-exact

    clone = await replay_delivery(db, org.id, d.id)
    assert clone.request_body == d.request_body
    await db.commit()

    owner_row = (
        await db.execute(select(OrgMember).where(OrgMember.org_id == org.id))
    ).scalars().first()
    user = await db.get(_User, owner_row.user_id)
    resp = await delivery_payload(org.id, d.id, db=db, user=user)
    assert resp.body.decode() == d.request_body

    other = await _org(db)
    other_owner_row = (
        await db.execute(select(OrgMember).where(OrgMember.org_id == other.id))
    ).scalars().first()
    other_user = await db.get(_User, other_owner_row.user_id)
    from app.exceptions import AppError

    with pytest.raises(AppError) as exc:
        await delivery_payload(other.id, d.id, db=db, user=other_user)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal", ["succeeded", "exhausted", "cancelled"])
async def test_terminal_delivery_redelivery_is_noop(db, egress, terminal):
    """Crash recovery can redeliver an outbox message after the delivery
    already reached a terminal state — the handler must no-op (no extra POST,
    no attempt-count bump, status unchanged)."""
    from app.integrations.models import DeliveryAttempt
    from app.integrations.services.events import handle_delivery_attempt

    org = await _org(db)
    await _sub(db, org)
    ev = await emit_event(db, org.id, "project.approved", subject="term", data={})
    await db.commit()
    await _drain(db)  # one real delivery to succeeded
    d = (
        await db.execute(select(EventDelivery).where(EventDelivery.event_id == ev.id))
    ).scalars().first()
    d.status = terminal
    await db.flush()
    calls_before = len(egress.calls)
    attempts_before = (
        await db.execute(
            select(DeliveryAttempt).where(DeliveryAttempt.delivery_id == d.id)
        )
    ).scalars().all()
    ac_before = d.attempt_count

    await handle_delivery_attempt(db, {"delivery_id": d.id})

    assert len(egress.calls) == calls_before  # no extra POST
    await db.refresh(d)
    assert d.status == terminal and d.attempt_count == ac_before
    attempts_after = (
        await db.execute(
            select(DeliveryAttempt).where(DeliveryAttempt.delivery_id == d.id)
        )
    ).scalars().all()
    assert len(attempts_after) == len(attempts_before)


@pytest.mark.asyncio
async def test_bulk_replay_exhausted(db):
    """R155: bulk replay requeues every exhausted delivery of a subscription,
    skips originals whose prior replay is in flight or already succeeded,
    refuses inactive subscriptions, and is cross-org invisible."""
    from app.exceptions import AppError
    from app.integrations.services.events import replay_exhausted

    org = await _org(db)
    sub = await _sub(db, org)
    evs = [
        await emit_event(db, org.id, "project.approved", subject=f"bulk-{i}", data={})
        for i in range(3)
    ]
    await db.flush()

    def mk(ev_id, status, replay_of=None):
        d = EventDelivery(
            event_id=ev_id, subscription_id=sub.id, status=status,
            attempt_count=5 if status == "exhausted" else 0,
            next_attempt_at=None, replay_of=replay_of, request_body="{}",
        )
        db.add(d)
        return d

    d1 = mk(evs[0].id, "exhausted")
    d2 = mk(evs[1].id, "exhausted")
    d3 = mk(evs[2].id, "exhausted")
    await db.flush()
    mk(evs[1].id, "succeeded", replay_of=d2.id)   # d2 already recovered
    mk(evs[2].id, "pending", replay_of=d3.id)     # d3 replay in flight
    await db.flush()

    clones = await replay_exhausted(db, org.id, sub.id)
    assert [c.replay_of for c in clones] == [d1.id]
    assert clones[0].status == "pending" and clones[0].attempt_count == 0
    assert clones[0].request_body == "{}"

    # second call: nothing left to requeue (d1 now covered by its clone)
    assert await replay_exhausted(db, org.id, sub.id) == []

    # inactive subscription refuses; cross-org is uniform 404
    sub.active = False
    await db.flush()
    with pytest.raises(AppError) as e:
        await replay_exhausted(db, org.id, sub.id)
    assert e.value.code == "DELIVERY_NOT_REPLAYABLE"
    other = await _org(db)
    with pytest.raises(AppError) as e2:
        await replay_exhausted(db, other.id, sub.id)
    assert e2.value.status_code == 404

"""Event mesh service: emit, fan out, deliver, replay (ADR-018 §12).

Flow:
  emit_event()            — intg_events row + cp_outbox 'intg.event.created'
                            in the CALLER's transaction (outbox pattern).
  handle_event_created()  — fan out to matching active webhook subscriptions:
                            one EventDelivery per match (ON CONFLICT no-op),
                            each with its own 'intg.delivery.attempt' message.
  handle_delivery_attempt() — sign (Standard Webhooks) + POST via the
                            EgressClient; success → succeeded; failure →
                            schedule the next ladder step via outbox
                            available_at, or exhaust after MAX_ATTEMPTS
                            (emits integration.delivery.exhausted + the
                            5-day consistent-failure auto-disable check).

Every handler is idempotent: deliveries are unique per (event, subscription);
an attempt message for a delivery that is no longer pending/delivering is a
no-op (covers outbox redelivery and replays racing retries).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time as _time
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    EVENT_NAMESPACE,
    INTERNAL_EVENT_PREFIX,
    MAX_ATTEMPTS,
    RETRY_OFFSETS_S,
    DeliveryAttempt,
    EventDelivery,
    IntegrationEvent,
)
from app.integrations.security import EgressClient
from app.models.webhook import WebhookSubscription

log = structlog.get_logger()

TOPIC_EVENT_CREATED = "intg.event.created"
TOPIC_DELIVERY_ATTEMPT = "intg.delivery.attempt"

# Previous secret keeps co-signing for this long after rotation (§12.2).
SECRET_PREV_WINDOW = timedelta(days=7)
# Consistent-failure window before auto-disabling an endpoint (Svix: 5 days).
AUTO_DISABLE_AFTER = timedelta(days=5)

_MAX_DATA_BYTES = 65_536


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ── emit (facade entry point) ──


async def emit_event(
    db: AsyncSession,
    org_id: str,
    event_type: str,
    *,
    subject: str | None = None,
    data: dict | None = None,
    version: int = 1,
) -> IntegrationEvent:
    """Append a canonical event + its outbox message in the caller's txn.

    ``event_type`` is the bare catalog name (e.g. "project.approved"); the
    stored CloudEvents type is namespaced + versioned:
    com.openskill.project.approved.v1. Fabric-internal names already carry
    the integration. prefix and are stored unversioned-namespaced as-is
    under the same reverse-DNS root.
    """
    payload = data or {}
    if len(json.dumps(payload)) > _MAX_DATA_BYTES:
        raise AppError("EVENT_DATA_TOO_LARGE", "event data exceeds 64KB", 422)
    full_type = f"{EVENT_NAMESPACE}{event_type}.v{version}"
    event = IntegrationEvent(
        org_id=org_id,
        type=full_type,
        source=f"/orgs/{org_id}",
        subject=subject,
        dataschema=f"/schemas/events/{full_type}.json",
        data=payload,
    )
    db.add(event)
    await db.flush()
    from app.controlplane.models.outbox import enqueue

    enqueue(db, TOPIC_EVENT_CREATED, {"event_id": event.id})
    return event


# ── subscription matching ──


def event_matches(patterns: list, event_type: str) -> bool:
    """Exact name or 'prefix.*' wildcard. Fabric-internal events
    (com.openskill.integration.*) match on EXACT name only — a wildcard must
    never route delivery-exhausted notices into the failing endpoint."""
    bare = event_type.removeprefix(EVENT_NAMESPACE)
    internal = bare.startswith(INTERNAL_EVENT_PREFIX)
    for p in patterns:
        if not isinstance(p, str):
            continue
        if p == event_type:
            return True
        if not internal and p.endswith(".*") and event_type.startswith(p[:-1]):
            return True
    return False


# ── outbox handlers ──


async def handle_event_created(db: AsyncSession, payload: dict) -> None:
    event = await db.get(IntegrationEvent, payload.get("event_id", ""))
    if event is None:  # event rolled back / purged — nothing to fan out
        return
    subs = (
        (
            await db.execute(
                select(WebhookSubscription).where(
                    WebhookSubscription.org_id == event.org_id,
                    WebhookSubscription.active.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )
    from app.controlplane.models.outbox import enqueue

    for sub in subs:
        if not event_matches(sub.events or [], event.type):
            continue
        # Idempotent fan-out: the unique (event, subscription) index makes a
        # redelivered outbox message a no-op.
        res = await db.execute(
            pg_insert(EventDelivery)
            .values(
                event_id=event.id,
                subscription_id=sub.id,
                status="pending",
                attempt_count=0,
                next_attempt_at=_utcnow(),
            )
            .on_conflict_do_nothing(
                index_elements=["event_id", "subscription_id"],
                index_where=EventDelivery.replay_of.is_(None),
            )
            .returning(EventDelivery.id)
        )
        delivery_id = res.scalar_one_or_none()
        if delivery_id is not None:
            enqueue(db, TOPIC_DELIVERY_ATTEMPT, {"delivery_id": delivery_id})


def sign_payload(secret: str, message_id: str, timestamp: int, body: bytes) -> str:
    """Standard Webhooks signature: base64(HMAC-SHA256(secret, id.ts.body))."""
    signed = f"{message_id}.{timestamp}.".encode() + body
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).digest()
    return "v1," + base64.b64encode(digest).decode()


def build_delivery_headers(
    sub: WebhookSubscription, event_id: str, body: bytes, now: datetime
) -> dict[str, str]:
    ts = int(now.timestamp())
    sigs = [sign_payload(sub.secret, event_id, ts, body)]
    if sub.secret_prev and sub.secret_rotated_at:
        rotated = sub.secret_rotated_at
        if rotated.tzinfo is None:
            rotated = rotated.replace(tzinfo=UTC)
        if now - rotated <= SECRET_PREV_WINDOW:
            sigs.append(sign_payload(sub.secret_prev, event_id, ts, body))
    return {
        "content-type": "application/json",
        "webhook-id": event_id,
        "webhook-timestamp": str(ts),
        "webhook-signature": " ".join(sigs),
    }


def _cloudevent_body(event: IntegrationEvent) -> bytes:
    return json.dumps(
        {
            "specversion": "1.0",
            "id": event.id,
            "source": event.source,
            "type": event.type,
            "subject": event.subject,
            "time": event.time.isoformat() if event.time else None,
            "dataschema": event.dataschema,
            "datacontenttype": "application/json",
            "data": event.data,
        },
        separators=(",", ":"),
    ).encode()


async def handle_delivery_attempt(db: AsyncSession, payload: dict) -> None:
    delivery = await db.get(EventDelivery, payload.get("delivery_id", ""))
    if delivery is None or delivery.status not in ("pending", "delivering"):
        return  # idempotent: replayed/cancelled/finished deliveries no-op
    sub = await db.get(WebhookSubscription, delivery.subscription_id)
    event = await db.get(IntegrationEvent, delivery.event_id)
    if sub is None or event is None or not sub.active:
        delivery.status = "cancelled"
        return

    delivery.status = "delivering"
    delivery.attempt_count += 1
    attempt_no = delivery.attempt_count
    body = _cloudevent_body(event)
    now = _utcnow()
    headers = build_delivery_headers(sub, event.id, body, now)

    started = _time.monotonic()
    status_code: int | None = None
    error: str | None = None
    try:
        resp = await EgressClient().request("POST", sub.url, headers=headers, content=body)
        status_code = resp.status_code
        if 200 <= resp.status_code < 300:
            delivery.status = "succeeded"
            delivery.next_attempt_at = None
        else:
            error = f"http_{resp.status_code}"
    except AppError as exc:
        error = exc.code[:200]
    except Exception as exc:  # network timeouts etc. — retryable
        error = type(exc).__name__[:200]

    db.add(
        DeliveryAttempt(
            delivery_id=delivery.id,
            status_code=status_code,
            error=error,
            latency_ms=int((_time.monotonic() - started) * 1000),
        )
    )

    if delivery.status == "succeeded":
        return

    if attempt_no >= MAX_ATTEMPTS:
        delivery.status = "exhausted"
        delivery.next_attempt_at = None
        # Alertable, first-class event (§12.2) — internal, exact-match fan-out.
        await emit_event(
            db,
            event.org_id,
            f"{INTERNAL_EVENT_PREFIX}delivery.exhausted",
            subject=delivery.id,
            data={"subscription_id": sub.id, "event_id": event.id, "last_error": error},
        )
        await _maybe_auto_disable(db, sub, now)
        return

    # Schedule the next ladder step via outbox available_at.
    delay_s = RETRY_OFFSETS_S[attempt_no - 1]
    delivery.status = "pending"
    delivery.next_attempt_at = now + timedelta(seconds=delay_s)
    from app.controlplane.models.outbox import enqueue

    enqueue(
        db,
        TOPIC_DELIVERY_ATTEMPT,
        {"delivery_id": delivery.id},
        available_at=delivery.next_attempt_at,
    )


async def _maybe_auto_disable(db: AsyncSession, sub: WebhookSubscription, now: datetime) -> None:
    """Svix rule: an endpoint failing consistently for 5 days is disabled.

    Implemented as: the earliest non-succeeded delivery AFTER the last
    success is ≥ 5 days old (and no success since). Deliveries are the
    evidence trail, so this is purely data-driven and replay-safe.
    """
    last_ok = (
        await db.execute(
            select(EventDelivery.updated_at)
            .where(
                EventDelivery.subscription_id == sub.id,
                EventDelivery.status == "succeeded",
            )
            .order_by(EventDelivery.updated_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    q = select(EventDelivery.created_at).where(
        EventDelivery.subscription_id == sub.id,
        EventDelivery.status == "exhausted",
    )
    if last_ok is not None:
        q = q.where(EventDelivery.created_at > last_ok)
    first_fail = (
        await db.execute(q.order_by(EventDelivery.created_at.asc()).limit(1))
    ).scalar_one_or_none()
    if first_fail is None:
        return
    if first_fail.tzinfo is None:
        first_fail = first_fail.replace(tzinfo=UTC)
    if now - first_fail >= AUTO_DISABLE_AFTER:
        sub.active = False
        await emit_event(
            db,
            sub.org_id,
            f"{INTERNAL_EVENT_PREFIX}subscription.auto_disabled",
            subject=sub.id,
            data={"reason": "consistent_failure_5d"},
        )
        log.warning("webhook_subscription_auto_disabled", subscription_id=sub.id)


# ── replay (§12.2) ──


async def replay_delivery(db: AsyncSession, org_id: str, delivery_id: str) -> EventDelivery:
    delivery = await db.get(EventDelivery, delivery_id)
    event = await db.get(IntegrationEvent, delivery.event_id) if delivery else None
    # Uniform 404: cross-tenant and unknown ids are indistinguishable.
    if delivery is None or event is None or event.org_id != org_id:
        raise AppError("DELIVERY_NOT_FOUND", "Delivery not found", 404)
    if delivery.status not in ("exhausted", "cancelled", "succeeded"):
        raise AppError("DELIVERY_NOT_REPLAYABLE", "Delivery is still in flight", 409)
    sub = await db.get(WebhookSubscription, delivery.subscription_id)
    if sub is None or not sub.active:
        raise AppError("DELIVERY_NOT_REPLAYABLE", "Subscription inactive", 409)
    # One in-flight replay per source delivery: a second replay while the
    # first is still pending/delivering is a 409, not a dup-spam vector.
    in_flight = (
        await db.execute(
            select(EventDelivery.id).where(
                EventDelivery.replay_of == delivery.id,
                EventDelivery.status.in_(("pending", "delivering")),
            )
        )
    ).scalar_one_or_none()
    if in_flight is not None:
        raise AppError("DELIVERY_NOT_REPLAYABLE", "A replay is already in flight", 409)
    clone = EventDelivery(
        event_id=delivery.event_id,
        subscription_id=delivery.subscription_id,
        status="pending",
        attempt_count=0,
        next_attempt_at=_utcnow(),
        replay_of=delivery.id,
    )
    db.add(clone)
    await db.flush()
    from app.controlplane.models.outbox import enqueue

    enqueue(db, TOPIC_DELIVERY_ATTEMPT, {"delivery_id": clone.id})
    await db.refresh(clone)
    return clone

"""App Webhook Event Router — fan-out event delivery to subscribed app endpoints.

Routes platform events to installed app webhook endpoints:
- Subscription matching: event type → subscribed apps
- Payload enrichment with org/user context
- Fan-out with per-app delivery isolation
- Filter evaluation (apps can subscribe to event subsets)
- Delivery manifest generation for the retry queue
- Event deduplication via idempotency keys
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class DeliveryPriority(str, Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class EventSubscription:
    """An app's subscription to a specific event type."""

    app_id: str
    app_name: str
    event_type: str         # e.g. "skill_pack.published"
    webhook_url: str
    secret: str
    org_id: str             # mandatory: installation scope, set server-side
    filters: dict | None = None  # e.g. {"category": "ai"}
    priority: DeliveryPriority = DeliveryPriority.NORMAL
    active: bool = True
    platform_scoped: bool = False  # admin-approved cross-org apps only


@dataclass
class PlatformEvent:
    """A platform event to route to subscribers."""

    event_id: str
    event_type: str
    payload: dict
    org_id: str | None = None
    user_id: str | None = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class DeliveryTarget:
    """A resolved delivery target for a specific event + subscriber."""

    event_id: str
    app_id: str
    app_name: str
    webhook_url: str
    secret: str
    enriched_payload: dict
    priority: DeliveryPriority
    idempotency_key: str


@dataclass
class RouteResult:
    """Result of routing an event to subscribers."""

    event_id: str
    event_type: str
    total_subscribers: int
    matched: int
    filtered_out: int
    duplicates_skipped: int
    targets: list[DeliveryTarget]


def _compute_idempotency_key(event_id: str, app_id: str) -> str:
    """Deterministic idempotency key: prevents duplicate delivery of the same event to the same app."""
    raw = f"{event_id}:{app_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


class AppWebhookEventRouter:
    """Route platform events to subscribed app webhook endpoints."""

    def __init__(self):
        # event_type → list of subscriptions
        self._subscriptions: dict[str, list[EventSubscription]] = defaultdict(list)
        # Set of delivered idempotency keys (for dedup)
        self._delivered: set[str] = set()
        # Stats
        self._total_routed = 0
        self._total_filtered = 0
        self._total_deduped = 0

    # ── Subscription management ──────────────────────────

    def subscribe(self, sub: EventSubscription) -> None:
        """Register an app's webhook subscription for an event type.

        Keyed by (app_id, org_id) — never overwrites a different org's subscription.
        org_id and platform_scoped are immutable after creation.
        """
        existing = self._subscriptions[sub.event_type]
        for s in existing:
            if s.app_id == sub.app_id and s.org_id == sub.org_id:
                # Update mutable fields in place (never org_id or platform_scoped)
                s.webhook_url = sub.webhook_url
                s.secret = sub.secret
                s.filters = sub.filters
                s.priority = sub.priority
                s.active = sub.active
                return
        self._subscriptions[sub.event_type].append(sub)

    def unsubscribe(self, app_id: str, event_type: str) -> bool:
        """Remove an app's subscription to an event type."""
        subs = self._subscriptions.get(event_type, [])
        before = len(subs)
        self._subscriptions[event_type] = [s for s in subs if s.app_id != app_id]
        return len(self._subscriptions[event_type]) < before

    def unsubscribe_app(self, app_id: str) -> int:
        """Remove all subscriptions for an app (e.g. on uninstall)."""
        total = 0
        for event_type in list(self._subscriptions.keys()):
            subs = self._subscriptions[event_type]
            before = len(subs)
            self._subscriptions[event_type] = [s for s in subs if s.app_id != app_id]
            total += before - len(self._subscriptions[event_type])
        return total

    def get_subscriptions(self, event_type: str) -> list[EventSubscription]:
        return [s for s in self._subscriptions.get(event_type, []) if s.active]

    def get_app_subscriptions(self, app_id: str) -> list[EventSubscription]:
        result = []
        for subs in self._subscriptions.values():
            result.extend(s for s in subs if s.app_id == app_id)
        return sorted(result, key=lambda s: s.event_type)

    # ── Routing ──────────────────────────────────────────

    def route(self, event: PlatformEvent) -> RouteResult:
        """Route an event to all matching subscribers.

        Returns a RouteResult with delivery targets ready for the retry queue.
        """
        subs = self.get_subscriptions(event.event_type)
        # Also check wildcard "*" subscriptions
        subs += self.get_subscriptions("*")

        targets: list[DeliveryTarget] = []
        filtered_out = 0
        deduped = 0

        for sub in subs:
            # Mandatory org-scope check: deny cross-tenant delivery
            # unless the app is explicitly platform-scoped (admin-approved)
            if not sub.platform_scoped:
                if not sub.org_id or not event.org_id or sub.org_id != event.org_id:
                    filtered_out += 1
                    continue

            # Evaluate additional filters
            if not self._matches_filter(sub.filters, event):
                filtered_out += 1
                continue

            # Dedup check
            idem_key = _compute_idempotency_key(event.event_id, sub.app_id)
            if idem_key in self._delivered:
                deduped += 1
                continue

            # Enrich payload
            enriched = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "occurred_at": event.occurred_at.isoformat(),
                "data": event.payload,
            }
            if event.org_id:
                enriched["org_id"] = event.org_id
            if event.user_id:
                enriched["user_id"] = event.user_id

            target = DeliveryTarget(
                event_id=event.event_id,
                app_id=sub.app_id,
                app_name=sub.app_name,
                webhook_url=sub.webhook_url,
                secret=sub.secret,
                enriched_payload=enriched,
                priority=sub.priority,
                idempotency_key=idem_key,
            )
            targets.append(target)
            self._delivered.add(idem_key)

        # Sort by priority (high first)
        priority_order = {DeliveryPriority.HIGH: 0, DeliveryPriority.NORMAL: 1, DeliveryPriority.LOW: 2}
        targets.sort(key=lambda t: priority_order.get(t.priority, 1))

        self._total_routed += len(targets)
        self._total_filtered += filtered_out
        self._total_deduped += deduped

        log.info(
            "event.routed",
            event_id=event.event_id,
            event_type=event.event_type,
            matched=len(targets),
            filtered=filtered_out,
        )

        return RouteResult(
            event_id=event.event_id,
            event_type=event.event_type,
            total_subscribers=len(subs),
            matched=len(targets),
            filtered_out=filtered_out,
            duplicates_skipped=deduped,
            targets=targets,
        )

    # ── Stats ────────────────────────────────────────────

    @property
    def stats(self) -> dict:
        return {
            "total_routed": self._total_routed,
            "total_filtered": self._total_filtered,
            "total_deduped": self._total_deduped,
            "subscription_count": sum(len(s) for s in self._subscriptions.values()),
        }

    # ── Internal ─────────────────────────────────────────

    @staticmethod
    def _matches_filter(filters: dict | None, event: PlatformEvent) -> bool:
        """Check if an event matches subscription filters.

        Fail-closed: if a filter key is not present in the event, the filter
        does NOT match (prevents accidental leakage when events lack a field).
        """
        if not filters:
            return True

        for key, expected in filters.items():
            if key == "org_id":
                if event.org_id != expected:
                    return False
            elif key == "user_id":
                if event.user_id != expected:
                    return False
            else:
                # Fail-closed: key must exist in payload AND match
                if key not in event.payload or event.payload[key] != expected:
                    return False

        return True

"""App Event Bus — publish-subscribe event routing for installed apps.

Manages in-memory pub/sub for app events:
- Subscribe handlers to event types
- Publish events to matching subscribers
- Wildcard subscriptions (subscribe to all events)
- Per-installation scoped subscriptions
- Event history for replay
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Event:
    """A published event."""

    event_id: str
    event_type: str
    payload: dict
    installation_id: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Subscription:
    """A subscription to event types."""

    subscription_id: str
    installation_id: str
    event_types: list[str] | None  # None = wildcard (all events)
    active: bool = True


@dataclass
class DeliveredEvent:
    """Record of an event delivered to a subscription."""

    event: Event
    subscription_id: str


class AppEventBus:
    """Publish-subscribe event routing for installed apps."""

    def __init__(self, history_limit: int = 1000) -> None:
        # (installation_id, subscription_id) → Subscription
        self._subs: dict[tuple[str, str], Subscription] = {}
        # Event history per installation
        self._history: dict[str, list[Event]] = {}
        self._history_limit = max(10, history_limit)
        # Delivered events for tracking
        self._delivered: list[DeliveredEvent] = []

    def subscribe(
        self,
        installation_id: str,
        subscription_id: str,
        event_types: list[str] | None = None,
    ) -> Subscription:
        """Create a subscription."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not subscription_id:
            raise ValueError("subscription_id is required")

        key = (installation_id, subscription_id)
        if key in self._subs:
            raise ValueError(f"Subscription {subscription_id} already exists")

        sub = Subscription(
            subscription_id=subscription_id,
            installation_id=installation_id,
            event_types=event_types,
        )
        self._subs[key] = sub
        return sub

    def unsubscribe(self, installation_id: str, subscription_id: str) -> None:
        """Remove a subscription."""
        key = (installation_id, subscription_id)
        if key not in self._subs:
            raise KeyError(f"Subscription {subscription_id} not found")
        del self._subs[key]

    def publish(self, event: Event) -> list[DeliveredEvent]:
        """Publish an event to matching subscribers."""
        if not event.installation_id:
            raise ValueError("installation_id is required")

        # Store in history
        history = self._history.setdefault(event.installation_id, [])
        history.append(event)
        if len(history) > self._history_limit:
            del history[:-self._history_limit]

        # Find matching subscriptions
        delivered: list[DeliveredEvent] = []
        for (inst, _), sub in self._subs.items():
            if inst != event.installation_id or not sub.active:
                continue
            if sub.event_types is None or event.event_type in sub.event_types:
                de = DeliveredEvent(event=event, subscription_id=sub.subscription_id)
                delivered.append(de)
                self._delivered.append(de)

        return delivered

    def get_history(
        self,
        installation_id: str,
        event_type: str | None = None,
        limit: int = 50,
    ) -> list[Event]:
        """Get event history, newest first."""
        events = self._history.get(installation_id, [])
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return list(reversed(events[-limit:]))

    def list_subscriptions(self, installation_id: str) -> list[Subscription]:
        return [
            sub for (inst, _), sub in self._subs.items()
            if inst == installation_id
        ]

    def get_delivery_count(self, installation_id: str, subscription_id: str) -> int:
        """Count events delivered to a subscription."""
        return sum(
            1 for de in self._delivered
            if de.event.installation_id == installation_id
            and de.subscription_id == subscription_id
        )

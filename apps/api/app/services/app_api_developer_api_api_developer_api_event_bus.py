"""App API Developer API Event Bus — internal event routing and subscription."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class EventSubscription:
    subscription_id: str
    event_pattern: str  # e.g. "user.*", "order.created"
    handler_url: str
    active: bool = True
    events_received: int = 0

@dataclass
class BusEvent:
    event_id: str
    event_type: str
    payload_size: int
    published_at: float = field(default_factory=time.time)
    subscribers_notified: int = 0

class AppAPIDeveloperAPIApiDeveloperApiEventBus:
    def __init__(self) -> None:
        self._subs: dict[tuple[str, str], EventSubscription] = {}
        self._events: dict[str, list[BusEvent]] = {}

    def subscribe(self, installation_id: str, subscription_id: str, event_pattern: str, handler_url: str) -> EventSubscription:
        if not installation_id: raise ValueError("installation_id is required")
        if not handler_url.startswith("https://"): raise ValueError("handler must use HTTPS")
        key = (installation_id, subscription_id)
        if key in self._subs: raise ValueError(f"Subscription {subscription_id} exists")
        s = EventSubscription(subscription_id=subscription_id, event_pattern=event_pattern, handler_url=handler_url)
        self._subs[key] = s
        return s

    def publish(self, installation_id: str, event_id: str, event_type: str, payload_size: int) -> BusEvent:
        if not installation_id: raise ValueError("installation_id is required")
        matching = self._match(installation_id, event_type)
        for sub in matching:
            sub.events_received += 1
        e = BusEvent(event_id=event_id, event_type=event_type, payload_size=payload_size, subscribers_notified=len(matching))
        self._events.setdefault(installation_id, []).append(e)
        return e

    def _match(self, installation_id: str, event_type: str) -> list[EventSubscription]:
        result = []
        for (inst, _), sub in self._subs.items():
            if inst != installation_id or not sub.active: continue
            pattern = sub.event_pattern
            if pattern == "*" or pattern == event_type: result.append(sub)
            elif pattern.endswith(".*") and event_type.startswith(pattern[:-2] + "."): result.append(sub)
        return result

    def unsubscribe(self, installation_id: str, subscription_id: str) -> None:
        key = (installation_id, subscription_id)
        sub = self._subs.get(key)
        if sub: sub.active = False

    def list_subscriptions(self, installation_id: str) -> list[EventSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id and s.active]

    def recent_events(self, installation_id: str, limit: int = 20) -> list[BusEvent]:
        return list(reversed(self._events.get(installation_id, [])[-limit:]))

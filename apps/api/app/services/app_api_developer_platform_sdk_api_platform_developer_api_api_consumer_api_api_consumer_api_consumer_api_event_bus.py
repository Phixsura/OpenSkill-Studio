"""Consumer API Event Bus — pub/sub event routing between consumers and services."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class EventSubscription:
    subscription_id: str
    consumer_id: str
    event_pattern: str  # "order.*", "user.created", "*"
    callback_url: str = ""
    active: bool = True

@dataclass
class Event:
    event_id: str
    event_type: str
    source: str
    payload: dict = field(default_factory=dict)
    published_at: datetime | None = None

@dataclass
class DeliveryRecord:
    event_id: str
    subscription_id: str
    consumer_id: str
    delivered: bool
    timestamp: datetime

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus:
    def __init__(self) -> None:
        self._subscriptions: dict[tuple[str, str], EventSubscription] = {}
        self._events: dict[tuple[str, str], list[Event]] = {}  # (inst, event_type)
        self._deliveries: list[DeliveryRecord] = []

    def subscribe(self, installation_id: str, sub: EventSubscription) -> EventSubscription:
        if not installation_id:
            raise ValueError("installation_id is required")
        if sub.callback_url and not sub.callback_url.startswith("https://"):
            raise ValueError("callback_url must use HTTPS")
        key = (installation_id, sub.subscription_id)
        self._subscriptions[key] = sub
        return sub

    def unsubscribe(self, installation_id: str, subscription_id: str) -> None:
        key = (installation_id, subscription_id)
        if key not in self._subscriptions:
            raise ValueError("Subscription not found")
        del self._subscriptions[key]

    def _matches(self, pattern: str, event_type: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")
        return pattern == event_type

    def publish(self, installation_id: str, event: Event, now: datetime | None = None) -> list[DeliveryRecord]:
        now = now or datetime.utcnow()
        event.published_at = now
        # Store event
        key = (installation_id, event.event_type)
        if key not in self._events:
            self._events[key] = []
        self._events[key].append(event)
        # Find matching subscriptions
        deliveries: list[DeliveryRecord] = []
        for (inst, _), sub in self._subscriptions.items():
            if inst != installation_id or not sub.active:
                continue
            if self._matches(sub.event_pattern, event.event_type):
                record = DeliveryRecord(event_id=event.event_id, subscription_id=sub.subscription_id, consumer_id=sub.consumer_id, delivered=True, timestamp=now)
                deliveries.append(record)
                self._deliveries.append(record)
        log.info("event_published", installation_id=installation_id, type=event.event_type, deliveries=len(deliveries))
        return deliveries

    def get_deliveries(self, installation_id: str, consumer_id: str, limit: int = 50) -> list[DeliveryRecord]:
        return [d for d in reversed(self._deliveries) if d.consumer_id == consumer_id][:limit]

    def list_subscriptions(self, installation_id: str, consumer_id: str | None = None) -> list[EventSubscription]:
        subs = [s for (inst, _), s in self._subscriptions.items() if inst == installation_id]
        if consumer_id:
            subs = [s for s in subs if s.consumer_id == consumer_id]
        return subs

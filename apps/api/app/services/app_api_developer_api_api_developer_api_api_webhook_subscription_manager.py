"""App API Developer Webhook Subscription Manager — manage topic-based subscriptions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WebhookSubscription:
    subscription_id: str
    topic: str
    callback_url: str
    active: bool = True
    created_at: float = field(default_factory=time.time)
    deliveries: int = 0
    failures: int = 0

    @property
    def success_rate(self) -> float:
        total = self.deliveries + self.failures
        return round(self.deliveries / total * 100, 1) if total > 0 else 100.0

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager:
    def __init__(self) -> None:
        self._subs: dict[tuple[str, str], WebhookSubscription] = {}

    def subscribe(self, installation_id: str, subscription_id: str, topic: str, callback_url: str) -> WebhookSubscription:
        if not installation_id: raise ValueError("installation_id is required")
        if not callback_url.startswith("https://"): raise ValueError("callback must use HTTPS")
        key = (installation_id, subscription_id)
        if key in self._subs: raise ValueError(f"Subscription {subscription_id} exists")
        s = WebhookSubscription(subscription_id=subscription_id, topic=topic, callback_url=callback_url)
        self._subs[key] = s
        return s

    def unsubscribe(self, installation_id: str, subscription_id: str) -> WebhookSubscription:
        key = (installation_id, subscription_id)
        s = self._subs.get(key)
        if s is None: raise KeyError(f"Subscription {subscription_id} not found")
        s.active = False
        return s

    def record_delivery(self, installation_id: str, subscription_id: str, success: bool) -> WebhookSubscription:
        key = (installation_id, subscription_id)
        s = self._subs.get(key)
        if s is None: raise KeyError(f"Subscription {subscription_id} not found")
        if success: s.deliveries += 1
        else: s.failures += 1
        return s

    def by_topic(self, installation_id: str, topic: str) -> list[WebhookSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id and s.topic == topic and s.active]

    def all_subscriptions(self, installation_id: str) -> list[WebhookSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id]

    def failing_subscriptions(self, installation_id: str, min_failure_rate: float = 10.0) -> list[WebhookSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id and s.active and (100 - s.success_rate) >= min_failure_rate]

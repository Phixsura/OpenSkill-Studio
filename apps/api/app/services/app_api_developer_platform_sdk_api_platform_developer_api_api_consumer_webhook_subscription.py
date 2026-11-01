"""API Consumer Webhook Subscription — manage webhook event subscriptions per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
from urllib.parse import urlparse
import time
import structlog

log = structlog.get_logger()

@dataclass
class WebhookSubscription:
    subscription_id: str
    consumer_id: str
    url: str
    events: list[str]  # ["order.created", "user.updated"]
    active: bool = True
    created_at: float = field(default_factory=time.time)
    secret: str = ""  # for signature verification

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscription:
    def __init__(self) -> None:
        self._subs: dict[tuple[str, str], WebhookSubscription] = {}

    def subscribe(self, installation_id: str, sub: WebhookSubscription) -> WebhookSubscription:
        if not installation_id: raise ValueError("installation_id is required")
        if not sub.events: raise ValueError("At least one event required")
        parsed = urlparse(sub.url)
        if parsed.scheme not in ("https",): raise ValueError("Webhook URL must use HTTPS")
        if not parsed.hostname: raise ValueError("Webhook URL must have hostname")
        key = (installation_id, sub.subscription_id)
        if key in self._subs: raise ValueError(f"Subscription {sub.subscription_id} exists")
        self._subs[key] = sub
        return sub

    def unsubscribe(self, installation_id: str, subscription_id: str) -> bool:
        key = (installation_id, subscription_id)
        if key in self._subs: del self._subs[key]; return True
        return False

    def toggle(self, installation_id: str, subscription_id: str, active: bool) -> WebhookSubscription:
        sub = self._get(installation_id, subscription_id)
        sub.active = active
        return sub

    def matches(self, installation_id: str, event_type: str) -> list[WebhookSubscription]:
        return [s for (inst, _), s in self._subs.items()
                if inst == installation_id and s.active and event_type in s.events]

    def list_subscriptions(self, installation_id: str, consumer_id: str | None = None) -> list[WebhookSubscription]:
        subs = [s for (inst, _), s in self._subs.items() if inst == installation_id]
        if consumer_id: subs = [s for s in subs if s.consumer_id == consumer_id]
        return subs

    def _get(self, installation_id: str, subscription_id: str) -> WebhookSubscription:
        s = self._subs.get((installation_id, subscription_id))
        if s is None: raise KeyError(f"Subscription {subscription_id} not found")
        return s

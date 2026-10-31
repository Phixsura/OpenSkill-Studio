"""App API Webhook Digest Subscription — subscribe to batched webhook digests."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DigestSubscription:
    subscription_id: str
    destination: str
    frequency: str  # "hourly", "daily", "weekly"
    event_types: list[str] = field(default_factory=list)
    enabled: bool = True
    digest_count: int = 0

VALID_FREQ = {"hourly", "daily", "weekly"}

class AppAPIWebhookDigestSubscription:
    def __init__(self) -> None:
        self._subs: dict[tuple[str, str], DigestSubscription] = {}

    def subscribe(self, installation_id: str, subscription_id: str, destination: str, frequency: str, event_types: list[str] | None = None) -> DigestSubscription:
        if not installation_id: raise ValueError("installation_id is required")
        if frequency not in VALID_FREQ: raise ValueError(f"frequency must be one of {VALID_FREQ}")
        key = (installation_id, subscription_id)
        if key in self._subs: raise ValueError(f"Subscription {subscription_id} exists")
        s = DigestSubscription(subscription_id=subscription_id, destination=destination, frequency=frequency, event_types=event_types or [])
        self._subs[key] = s
        return s

    def record_digest(self, installation_id: str, subscription_id: str) -> DigestSubscription:
        s = self._get(installation_id, subscription_id)
        s.digest_count += 1
        return s

    def toggle(self, installation_id: str, subscription_id: str, enabled: bool) -> DigestSubscription:
        s = self._get(installation_id, subscription_id)
        s.enabled = enabled
        return s

    def active_subscriptions(self, installation_id: str) -> list[DigestSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id and s.enabled]

    def list_subscriptions(self, installation_id: str) -> list[DigestSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id]

    def _get(self, installation_id: str, subscription_id: str) -> DigestSubscription:
        s = self._subs.get((installation_id, subscription_id))
        if s is None: raise KeyError(f"Subscription {subscription_id} not found")
        return s

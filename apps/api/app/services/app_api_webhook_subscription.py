"""App API Webhook Subscription — manage event subscriptions.

Manages webhook subscriptions:
- Subscribe to specific event patterns
- Wildcard event matching
- Enable/disable subscriptions
- Per-installation scoped subscriptions
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class WebhookSubscription:
    """A webhook event subscription."""

    subscription_id: str
    url: str
    event_pattern: str  # "push", "issue.*", "*"
    enabled: bool = True
    delivery_count: int = 0


class AppAPIWebhookSubscription:
    """Manage event subscriptions."""

    def __init__(self) -> None:
        self._subs: dict[tuple[str, str], WebhookSubscription] = {}

    def subscribe(
        self, installation_id: str, subscription_id: str,
        url: str, event_pattern: str,
    ) -> WebhookSubscription:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not url:
            raise ValueError("url is required")

        key = (installation_id, subscription_id)
        if key in self._subs:
            raise ValueError(f"Subscription {subscription_id} already exists")

        sub = WebhookSubscription(
            subscription_id=subscription_id, url=url, event_pattern=event_pattern,
        )
        self._subs[key] = sub
        return sub

    def matches(self, installation_id: str, event_type: str) -> list[WebhookSubscription]:
        """Find subscriptions matching an event type."""
        result = []
        for (inst, _), sub in self._subs.items():
            if inst != installation_id or not sub.enabled:
                continue
            if self._pattern_matches(sub.event_pattern, event_type):
                result.append(sub)
        return result

    def record_delivery(self, installation_id: str, subscription_id: str) -> WebhookSubscription:
        sub = self._get(installation_id, subscription_id)
        sub.delivery_count += 1
        return sub

    def toggle(self, installation_id: str, subscription_id: str, enabled: bool) -> WebhookSubscription:
        sub = self._get(installation_id, subscription_id)
        sub.enabled = enabled
        return sub

    def list_subscriptions(self, installation_id: str) -> list[WebhookSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id]

    def _get(self, installation_id: str, subscription_id: str) -> WebhookSubscription:
        key = (installation_id, subscription_id)
        s = self._subs.get(key)
        if s is None:
            raise KeyError(f"Subscription {subscription_id} not found")
        return s

    def _pattern_matches(self, pattern: str, event_type: str) -> bool:
        if pattern == "*":
            return True
        if pattern == event_type:
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")
        return False

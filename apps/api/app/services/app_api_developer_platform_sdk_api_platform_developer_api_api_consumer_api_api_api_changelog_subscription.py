"""API Consumer Changelog Subscription — subscribe consumers to API changelog updates."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogSubscription:
    consumer_id: str
    channels: list[str] = field(default_factory=lambda: ["email"])  # "email", "webhook", "in_app"
    categories: list[str] = field(default_factory=list)  # empty = all
    active: bool = True
    notifications_sent: int = 0

VALID_CHANNELS = {"email", "webhook", "in_app", "slack"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscription:
    def __init__(self) -> None:
        self._subs: dict[tuple[str, str], ChangelogSubscription] = {}

    def subscribe(self, installation_id: str, sub: ChangelogSubscription) -> ChangelogSubscription:
        if not installation_id: raise ValueError("installation_id is required")
        invalid = set(sub.channels) - VALID_CHANNELS
        if invalid: raise ValueError(f"Invalid channels: {invalid}")
        if not sub.channels: raise ValueError("At least one channel required")
        self._subs[(installation_id, sub.consumer_id)] = sub
        return sub

    def unsubscribe(self, installation_id: str, consumer_id: str) -> bool:
        key = (installation_id, consumer_id)
        sub = self._subs.get(key)
        if sub: sub.active = False; return True
        return False

    def notify(self, installation_id: str, category: str) -> int:
        """Notify matching subscribers. Returns count notified."""
        count = 0
        for (inst, _), sub in self._subs.items():
            if inst == installation_id and sub.active:
                if not sub.categories or category in sub.categories:
                    sub.notifications_sent += 1
                    count += 1
        return count

    def active_subscribers(self, installation_id: str) -> list[ChangelogSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id and s.active]

    def list_subs(self, installation_id: str) -> list[ChangelogSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id]

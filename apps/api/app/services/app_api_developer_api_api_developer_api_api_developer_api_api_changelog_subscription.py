"""App API Developer Changelog Subscription — subscribe to API change notifications."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogSubscription:
    subscription_id: str
    developer_id: str
    channels: list[str]  # "email", "webhook", "slack", "in_app"
    filters: list[str] = field(default_factory=list)  # "breaking", "feature", "fix", "deprecation"
    active: bool = True
    notifications_sent: int = 0
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription:
    def __init__(self) -> None:
        self._subs: dict[tuple[str, str], ChangelogSubscription] = {}

    def subscribe(self, installation_id: str, subscription_id: str, developer_id: str, channels: list[str], filters: list[str] | None = None) -> ChangelogSubscription:
        if not installation_id: raise ValueError("installation_id is required")
        valid_channels = {"email", "webhook", "slack", "in_app"}
        invalid = set(channels) - valid_channels
        if invalid: raise ValueError(f"Invalid channels: {invalid}")
        if not channels: raise ValueError("At least one channel required")
        key = (installation_id, subscription_id)
        if key in self._subs: raise ValueError(f"Subscription {subscription_id} exists")
        s = ChangelogSubscription(subscription_id=subscription_id, developer_id=developer_id, channels=channels, filters=filters or [])
        self._subs[key] = s
        return s

    def notify(self, installation_id: str, change_type: str) -> list[ChangelogSubscription]:
        matched = []
        for (inst, _), s in self._subs.items():
            if inst != installation_id or not s.active: continue
            if not s.filters or change_type in s.filters:
                s.notifications_sent += 1
                matched.append(s)
        return matched

    def unsubscribe(self, installation_id: str, subscription_id: str) -> ChangelogSubscription:
        key = (installation_id, subscription_id)
        s = self._subs.get(key)
        if s is None: raise KeyError(f"Subscription {subscription_id} not found")
        s.active = False
        return s

    def active_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _), s in self._subs.items() if inst == installation_id and s.active)

    def by_developer(self, installation_id: str, developer_id: str) -> list[ChangelogSubscription]:
        return [s for (inst, _), s in self._subs.items() if inst == installation_id and s.developer_id == developer_id]

"""App Changelog Subscriber — manage user subscriptions to app changelog updates.

Manages changelog notification subscriptions:
- Subscribe/unsubscribe users to changelog updates
- Track notification delivery per subscriber
- Filter by release types (major, minor, patch, security)
- Per-installation scoped subscriptions
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Subscriber:
    """A changelog subscriber."""

    subscriber_id: str
    installation_id: str
    channel: str  # "email", "webhook", "in_app"
    target: str   # email address, URL, user_id
    release_types: list[str] | None = None  # None = all
    active: bool = True
    subscribed_at: float = field(default_factory=time.time)
    last_notified_at: float | None = None
    notification_count: int = 0


@dataclass
class NotifyResult:
    """Result of notifying subscribers about a release."""

    release_version: str
    notified: list[str]  # subscriber_ids
    skipped: list[str]


class AppChangelogSubscriber:
    """Manage changelog notification subscriptions."""

    def __init__(self) -> None:
        self._subscribers: dict[tuple[str, str], Subscriber] = {}

    def subscribe(
        self,
        installation_id: str,
        subscriber_id: str,
        channel: str,
        target: str,
        release_types: list[str] | None = None,
    ) -> Subscriber:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not subscriber_id:
            raise ValueError("subscriber_id is required")
        if not channel:
            raise ValueError("channel is required")
        if not target:
            raise ValueError("target is required")

        key = (installation_id, subscriber_id)
        if key in self._subscribers:
            raise ValueError(f"Subscriber {subscriber_id} already exists")

        sub = Subscriber(
            subscriber_id=subscriber_id,
            installation_id=installation_id,
            channel=channel,
            target=target,
            release_types=release_types,
        )
        self._subscribers[key] = sub
        return sub

    def unsubscribe(self, installation_id: str, subscriber_id: str) -> None:
        key = (installation_id, subscriber_id)
        if key not in self._subscribers:
            raise KeyError(f"Subscriber {subscriber_id} not found")
        self._subscribers[key].active = False

    def notify_release(
        self,
        installation_id: str,
        release_version: str,
        release_type: str = "minor",
        now: float | None = None,
    ) -> NotifyResult:
        """Notify matching subscribers about a release."""
        now = now or time.time()
        notified: list[str] = []
        skipped: list[str] = []

        for (inst, _), sub in self._subscribers.items():
            if inst != installation_id:
                continue
            if not sub.active:
                skipped.append(sub.subscriber_id)
                continue
            if sub.release_types and release_type not in sub.release_types:
                skipped.append(sub.subscriber_id)
                continue

            sub.last_notified_at = now
            sub.notification_count += 1
            notified.append(sub.subscriber_id)

        return NotifyResult(
            release_version=release_version,
            notified=notified,
            skipped=skipped,
        )

    def list_subscribers(self, installation_id: str, active_only: bool = True) -> list[Subscriber]:
        subs = [s for (inst, _), s in self._subscribers.items() if inst == installation_id]
        if active_only:
            subs = [s for s in subs if s.active]
        return subs

    def get_subscriber(self, installation_id: str, subscriber_id: str) -> Subscriber:
        key = (installation_id, subscriber_id)
        sub = self._subscribers.get(key)
        if sub is None:
            raise KeyError(f"Subscriber {subscriber_id} not found")
        return sub

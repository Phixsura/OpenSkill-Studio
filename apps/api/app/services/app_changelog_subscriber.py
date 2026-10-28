"""App Changelog Subscriber — manage changelog notification subscribers.

Manages changelog subscribers:
- Subscribe users/emails to changelog updates
- Unsubscribe with confirmation
- Deliver changelog notifications
- Per-installation scoped subscribers
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
    email: str
    name: str = ""
    subscribed_at: float = field(default_factory=time.time)
    active: bool = True
    delivery_count: int = 0


class AppChangelogSubscriber:
    """Manage changelog notification subscribers."""

    def __init__(self) -> None:
        self._subscribers: dict[tuple[str, str], Subscriber] = {}

    def subscribe(
        self, installation_id: str, subscriber_id: str, email: str, name: str = "",
    ) -> Subscriber:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not email or "@" not in email:
            raise ValueError("valid email is required")

        # Prevent duplicate emails
        for (inst, _), s in self._subscribers.items():
            if inst == installation_id and s.email == email and s.active:
                raise ValueError(f"Email {email} already subscribed")

        sub = Subscriber(subscriber_id=subscriber_id, email=email, name=name)
        self._subscribers[(installation_id, subscriber_id)] = sub
        return sub

    def unsubscribe(self, installation_id: str, subscriber_id: str) -> Subscriber:
        key = (installation_id, subscriber_id)
        s = self._subscribers.get(key)
        if s is None:
            raise KeyError(f"Subscriber {subscriber_id} not found")
        s.active = False
        return s

    def record_delivery(self, installation_id: str, subscriber_id: str) -> Subscriber:
        key = (installation_id, subscriber_id)
        s = self._subscribers.get(key)
        if s is None:
            raise KeyError(f"Subscriber {subscriber_id} not found")
        s.delivery_count += 1
        return s

    def active_subscribers(self, installation_id: str) -> list[Subscriber]:
        return [
            s for (inst, _), s in self._subscribers.items()
            if inst == installation_id and s.active
        ]

    def count(self, installation_id: str) -> int:
        return len(self.active_subscribers(installation_id))

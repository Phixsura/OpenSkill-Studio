"""API Consumer Notification Digest — aggregate notifications into periodic digests."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class Notification:
    notification_id: str
    category: str  # "alert", "changelog", "billing", "security", "usage"
    title: str
    message: str = ""
    severity: str = "info"  # "info", "warning", "critical"
    timestamp: float = field(default_factory=time.time)

@dataclass
class Digest:
    digest_id: str
    consumer_id: str
    period: str
    notifications: list[Notification] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)

    @property
    def by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for n in self.notifications: counts[n.category] = counts.get(n.category, 0) + 1
        return counts

VALID_CATEGORIES = {"alert", "changelog", "billing", "security", "usage", "system"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiNotificationDigest:
    def __init__(self) -> None:
        self._notifications: dict[tuple[str, str], list[Notification]] = {}
        self._digests: dict[tuple[str, str], list[Digest]] = {}

    def add_notification(self, installation_id: str, consumer_id: str, notification: Notification) -> Notification:
        if not installation_id: raise ValueError("installation_id is required")
        if notification.category not in VALID_CATEGORIES: raise ValueError(f"Invalid category: {notification.category}")
        self._notifications.setdefault((installation_id, consumer_id), []).append(notification)
        return notification

    def generate_digest(self, installation_id: str, consumer_id: str, digest_id: str, period: str) -> Digest:
        key = (installation_id, consumer_id)
        notifications = self._notifications.get(key, [])
        digest = Digest(digest_id=digest_id, consumer_id=consumer_id, period=period, notifications=list(notifications))
        self._digests.setdefault(key, []).append(digest)
        self._notifications[key] = []  # clear after digest
        return digest

    def unread_count(self, installation_id: str, consumer_id: str) -> int:
        return len(self._notifications.get((installation_id, consumer_id), []))

    def recent_digests(self, installation_id: str, consumer_id: str, limit: int = 5) -> list[Digest]:
        return list(reversed(self._digests.get((installation_id, consumer_id), [])[-limit:]))

    def notification_count(self, installation_id: str) -> int:
        return sum(len(n) for (inst, _), n in self._notifications.items() if inst == installation_id)

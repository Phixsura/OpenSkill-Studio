"""App API Changelog Notification — notify subscribers of new changelogs."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class NotificationRecord:
    notification_id: str
    version: str
    channel: str  # "email", "slack", "webhook"
    recipient_count: int
    sent_at: float = field(default_factory=time.time)
    delivered: int = 0
    failed: int = 0

class AppAPIChangelogNotification:
    def __init__(self) -> None:
        self._notifications: dict[str, list[NotificationRecord]] = {}

    def send(self, installation_id: str, notification_id: str, version: str, channel: str, recipient_count: int) -> NotificationRecord:
        if not installation_id: raise ValueError("installation_id is required")
        if channel not in ("email", "slack", "webhook"): raise ValueError("channel must be email, slack, or webhook")
        n = NotificationRecord(notification_id=notification_id, version=version, channel=channel, recipient_count=recipient_count)
        self._notifications.setdefault(installation_id, []).append(n)
        return n

    def record_delivery(self, installation_id: str, notification_id: str, delivered: int, failed: int) -> NotificationRecord:
        for n in self._notifications.get(installation_id, []):
            if n.notification_id == notification_id:
                n.delivered = delivered
                n.failed = failed
                return n
        raise KeyError(f"Notification {notification_id} not found")

    def recent(self, installation_id: str, limit: int = 20) -> list[NotificationRecord]:
        return list(reversed(self._notifications.get(installation_id, [])[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._notifications.get(installation_id, []))

"""App API Developer Notification Center — unified notification hub."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class CenterNotification:
    notification_id: str
    title: str
    body: str
    category: str  # "system", "changelog", "incident", "security", "billing"
    read: bool = False
    created_at: float = field(default_factory=time.time)

VALID_CATEGORIES = {"system", "changelog", "incident", "security", "billing"}

class AppAPIDeveloperAPINotificationCenter:
    def __init__(self) -> None:
        self._notifications: dict[str, list[CenterNotification]] = {}

    def send(self, installation_id: str, notification_id: str, title: str, body: str, category: str) -> CenterNotification:
        if not installation_id: raise ValueError("installation_id is required")
        if category not in VALID_CATEGORIES: raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        n = CenterNotification(notification_id=notification_id, title=title, body=body, category=category)
        self._notifications.setdefault(installation_id, []).append(n)
        return n

    def mark_read(self, installation_id: str, notification_id: str) -> CenterNotification:
        for n in self._notifications.get(installation_id, []):
            if n.notification_id == notification_id:
                n.read = True
                return n
        raise KeyError(f"Notification {notification_id} not found")

    def unread_count(self, installation_id: str) -> int:
        return sum(1 for n in self._notifications.get(installation_id, []) if not n.read)

    def by_category(self, installation_id: str, category: str) -> list[CenterNotification]:
        return [n for n in self._notifications.get(installation_id, []) if n.category == category]

    def recent(self, installation_id: str, limit: int = 20) -> list[CenterNotification]:
        return list(reversed(self._notifications.get(installation_id, [])[-limit:]))

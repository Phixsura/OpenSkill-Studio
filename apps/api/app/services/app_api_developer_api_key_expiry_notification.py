"""App API Developer API Key Expiry Notification — notify about expiring keys."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ExpiryNotification:
    notification_id: str
    key_id: str
    developer_id: str
    days_until_expiry: int
    sent: bool = False

class AppAPIDeveloperAPIKeyExpiryNotification:
    def __init__(self) -> None:
        self._notifications: dict[tuple[str, str], ExpiryNotification] = {}

    def create(self, installation_id: str, notification_id: str, key_id: str, developer_id: str, days_until_expiry: int) -> ExpiryNotification:
        if not installation_id: raise ValueError("installation_id is required")
        if days_until_expiry < 0: raise ValueError("days must be non-negative")
        n = ExpiryNotification(notification_id=notification_id, key_id=key_id, developer_id=developer_id, days_until_expiry=days_until_expiry)
        self._notifications[(installation_id, notification_id)] = n
        return n

    def mark_sent(self, installation_id: str, notification_id: str) -> ExpiryNotification:
        n = self._notifications.get((installation_id, notification_id))
        if n is None: raise KeyError(f"Notification {notification_id} not found")
        n.sent = True
        return n

    def pending(self, installation_id: str) -> list[ExpiryNotification]:
        return [n for (inst, _), n in self._notifications.items() if inst == installation_id and not n.sent]

    def urgent(self, installation_id: str, threshold_days: int = 7) -> list[ExpiryNotification]:
        return [n for (inst, _), n in self._notifications.items() if inst == installation_id and n.days_until_expiry <= threshold_days and not n.sent]

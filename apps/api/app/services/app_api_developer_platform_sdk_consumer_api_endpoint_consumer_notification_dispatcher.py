"""Consumer API Notification Dispatcher — dispatch notifications across channels."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class Notification:
    notification_id: str
    consumer_id: str
    title: str
    message: str
    severity: str = "info"  # "info", "warning", "critical"
    channels: list[str] = field(default_factory=list)  # "email", "slack", "in_app", "webhook"
    dispatched_at: datetime | None = None
    read: bool = False

@dataclass
class DispatchResult:
    notification_id: str
    channels_sent: list[str]
    channels_failed: list[str]
    success: bool

VALID_CHANNELS = {"email", "slack", "in_app", "webhook", "sms"}
VALID_SEVERITIES = {"info", "warning", "critical"}

class AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher:
    def __init__(self) -> None:
        self._notifications: dict[tuple[str, str], list[Notification]] = {}
        self._channel_config: dict[tuple[str, str], set[str]] = {}

    def configure_channels(self, installation_id: str, consumer_id: str, channels: list[str]) -> list[str]:
        if not installation_id:
            raise ValueError("installation_id is required")
        for ch in channels:
            if ch not in VALID_CHANNELS:
                raise ValueError(f"Invalid channel: {ch}")
        self._channel_config[(installation_id, consumer_id)] = set(channels)
        return channels

    def dispatch(self, installation_id: str, notification: Notification, now: datetime) -> DispatchResult:
        if notification.severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {notification.severity}")
        configured = self._channel_config.get((installation_id, notification.consumer_id), {"in_app"})
        channels_to_use = [ch for ch in notification.channels if ch in configured] if notification.channels else list(configured)
        notification.dispatched_at = now
        key = (installation_id, notification.consumer_id)
        if key not in self._notifications:
            self._notifications[key] = []
        self._notifications[key].append(notification)
        if len(self._notifications[key]) > 1000:
            self._notifications[key] = self._notifications[key][-1000:]
        return DispatchResult(notification_id=notification.notification_id, channels_sent=channels_to_use, channels_failed=[], success=True)

    def mark_read(self, installation_id: str, consumer_id: str, notification_id: str) -> Notification | None:
        for n in self._notifications.get((installation_id, consumer_id), []):
            if n.notification_id == notification_id:
                n.read = True
                return n
        return None

    def get_unread(self, installation_id: str, consumer_id: str) -> list[Notification]:
        return [n for n in self._notifications.get((installation_id, consumer_id), []) if not n.read]

    def get_recent(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[Notification]:
        return list(reversed(self._notifications.get((installation_id, consumer_id), [])[-limit:]))

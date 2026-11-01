"""Consumer API Notification Channel — manage multi-channel notification delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class NotificationChannel:
    channel_id: str
    consumer_id: str
    channel_type: str  # "email", "webhook", "slack", "sms", "in_app"
    destination: str  # email address, URL, channel ID, phone
    verified: bool = False
    enabled: bool = True

@dataclass
class Notification:
    notification_id: str
    consumer_id: str
    channel_id: str
    title: str
    message: str
    severity: str = "info"  # "info", "warning", "critical"
    sent_at: datetime | None = None
    delivered: bool = False

VALID_TYPES = {"email", "webhook", "slack", "sms", "in_app"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel:
    def __init__(self) -> None:
        self._channels: dict[tuple[str, str, str], NotificationChannel] = {}
        self._notifications: dict[tuple[str, str], list[Notification]] = {}

    def add_channel(self, installation_id: str, channel: NotificationChannel) -> NotificationChannel:
        if not installation_id:
            raise ValueError("installation_id is required")
        if channel.channel_type not in VALID_TYPES:
            raise ValueError(f"Invalid type: {channel.channel_type}")
        if channel.channel_type == "webhook" and not channel.destination.startswith("https://"):
            raise ValueError("Webhook destination must use HTTPS")
        self._channels[(installation_id, channel.consumer_id, channel.channel_id)] = channel
        return channel

    def verify(self, installation_id: str, consumer_id: str, channel_id: str) -> NotificationChannel:
        key = (installation_id, consumer_id, channel_id)
        ch = self._channels.get(key)
        if not ch:
            raise ValueError("Channel not found")
        ch.verified = True
        return ch

    def send(self, installation_id: str, notification: Notification, now: datetime) -> Notification:
        key = (installation_id, notification.consumer_id, notification.channel_id)
        ch = self._channels.get(key)
        if not ch:
            raise ValueError("Channel not found")
        if not ch.enabled:
            raise ValueError("Channel disabled")
        if not ch.verified:
            raise ValueError("Channel not verified")
        notification.sent_at = now
        notification.delivered = True
        nkey = (installation_id, notification.consumer_id)
        if nkey not in self._notifications:
            self._notifications[nkey] = []
        self._notifications[nkey].append(notification)
        return notification

    def get_notifications(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[Notification]:
        return self._notifications.get((installation_id, consumer_id), [])[-limit:]

    def list_channels(self, installation_id: str, consumer_id: str) -> list[NotificationChannel]:
        return [c for (inst, cid, _), c in self._channels.items() if inst == installation_id and cid == consumer_id]

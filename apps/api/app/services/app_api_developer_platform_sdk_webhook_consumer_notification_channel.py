"""App API Developer Webhook Consumer Notification Channel — manage notification channels."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class NotificationChannel:
    channel_id: str
    consumer_id: str
    channel_type: str  # "email", "slack", "pagerduty", "webhook", "sms"
    target: str  # email address, webhook URL, channel ID
    enabled: bool = True
    notifications_sent: int = 0

class AppAPIDeveloperPlatformSDKWebhookConsumerNotificationChannel:
    def __init__(self) -> None:
        self._channels: dict[tuple[str, str], NotificationChannel] = {}

    def add(self, installation_id: str, channel_id: str, consumer_id: str, channel_type: str, target: str) -> NotificationChannel:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"email", "slack", "pagerduty", "webhook", "sms"}
        if channel_type not in valid: raise ValueError(f"Invalid channel: {channel_type}")
        if channel_type == "webhook" and not target.startswith("https://"): raise ValueError("webhook must use HTTPS")
        key = (installation_id, channel_id)
        if key in self._channels: raise ValueError(f"Channel {channel_id} exists")
        c = NotificationChannel(channel_id=channel_id, consumer_id=consumer_id, channel_type=channel_type, target=target)
        self._channels[key] = c
        return c

    def notify(self, installation_id: str, channel_id: str) -> NotificationChannel:
        key = (installation_id, channel_id)
        c = self._channels.get(key)
        if c is None: raise KeyError(f"Channel {channel_id} not found")
        if not c.enabled: raise ValueError("Channel is disabled")
        c.notifications_sent += 1
        return c

    def for_consumer(self, installation_id: str, consumer_id: str) -> list[NotificationChannel]:
        return [c for (inst, _), c in self._channels.items() if inst == installation_id and c.consumer_id == consumer_id and c.enabled]

    def all_channels(self, installation_id: str) -> list[NotificationChannel]:
        return [c for (inst, _), c in self._channels.items() if inst == installation_id]

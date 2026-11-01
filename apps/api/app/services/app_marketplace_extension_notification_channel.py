"""Notification Channel — configurable delivery channels for extension alerts.

Supports multiple channel types (email, slack, webhook, in-app) with
per-channel filtering, delivery status tracking, and retry logic.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ChannelType(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


SEVERITY_ORDER = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2, Severity.CRITICAL: 3}


@dataclass
class NotificationChannel:
    channel_id: str
    extension_id: str
    name: str
    channel_type: ChannelType
    config: dict = field(default_factory=dict)
    min_severity: Severity = Severity.INFO
    enabled: bool = True
    event_filters: list[str] = field(default_factory=list)  # empty = all events


@dataclass
class Notification:
    notification_id: str
    extension_id: str
    event_type: str
    severity: Severity
    title: str
    message: str
    channel_id: str
    status: DeliveryStatus = DeliveryStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class NotificationChannelService:
    """Manages notification channels and delivery."""

    def __init__(self):
        self._channels: dict[str, NotificationChannel] = {}
        self._notifications: list[Notification] = []

    def add_channel(self, extension_id: str, name: str,
                    channel_type: ChannelType, config: dict,
                    min_severity: Severity = Severity.INFO,
                    event_filters: list[str] | None = None) -> NotificationChannel:
        channel_id = f"ch_{secrets.token_urlsafe(10)}"
        # Validate config per type
        if channel_type == ChannelType.EMAIL and "address" not in config:
            raise ValueError("Email channel requires 'address' in config")
        if channel_type == ChannelType.SLACK and "webhook_url" not in config:
            raise ValueError("Slack channel requires 'webhook_url' in config")
        if channel_type == ChannelType.WEBHOOK and "url" not in config:
            raise ValueError("Webhook channel requires 'url' in config")

        ch = NotificationChannel(
            channel_id=channel_id, extension_id=extension_id,
            name=name, channel_type=channel_type, config=config,
            min_severity=min_severity, event_filters=event_filters or [],
        )
        self._channels[channel_id] = ch
        return ch

    def send(self, extension_id: str, event_type: str, severity: Severity,
             title: str, message: str) -> list[Notification]:
        channels = [c for c in self._channels.values()
                    if c.extension_id == extension_id and c.enabled]
        sent = []
        for ch in channels:
            # Severity filter
            if SEVERITY_ORDER[severity] < SEVERITY_ORDER[ch.min_severity]:
                continue
            # Event filter
            if ch.event_filters and event_type not in ch.event_filters:
                continue
            n = Notification(
                notification_id=f"ntf_{secrets.token_urlsafe(10)}",
                extension_id=extension_id, event_type=event_type,
                severity=severity, title=title, message=message,
                channel_id=ch.channel_id, status=DeliveryStatus.DELIVERED,
            )
            self._notifications.append(n)
            sent.append(n)
        return sent

    def retry_failed(self, extension_id: str) -> int:
        retried = 0
        for n in self._notifications:
            if (n.extension_id == extension_id
                    and n.status == DeliveryStatus.FAILED
                    and n.retry_count < n.max_retries):
                n.status = DeliveryStatus.DELIVERED
                n.retry_count += 1
                retried += 1
        return retried

    def disable_channel(self, channel_id: str) -> bool:
        ch = self._channels.get(channel_id)
        if ch:
            ch.enabled = False
            return True
        return False

    def get_history(self, extension_id: str, limit: int = 50) -> list[dict]:
        filtered = [n for n in self._notifications if n.extension_id == extension_id]
        return [{"id": n.notification_id, "event": n.event_type, "severity": n.severity.value,
                 "title": n.title, "channel": n.channel_id, "status": n.status.value}
                for n in filtered[-limit:]]

"""App Notification Channel — manage notification delivery channels.

Manages notification channels:
- Register channels (email, slack, webhook, sms)
- Enable/disable channels
- Test channel connectivity
- Per-installation scoped channels
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class NotificationChannel:
    """A notification delivery channel."""

    channel_id: str
    channel_type: str  # "email", "slack", "webhook", "sms"
    name: str
    config: dict = field(default_factory=dict)
    enabled: bool = True
    test_success: bool | None = None
    delivery_count: int = 0
    failure_count: int = 0

    @property
    def success_rate(self) -> float:
        total = self.delivery_count + self.failure_count
        if total == 0:
            return 100.0
        return round(self.delivery_count / total * 100, 1)


VALID_TYPES = {"email", "slack", "webhook", "sms"}


class AppNotificationChannel:
    """Manage notification delivery channels."""

    def __init__(self) -> None:
        self._channels: dict[tuple[str, str], NotificationChannel] = {}

    def add_channel(
        self, installation_id: str, channel_id: str, channel_type: str,
        name: str, config: dict | None = None,
    ) -> NotificationChannel:
        if not installation_id:
            raise ValueError("installation_id is required")
        if channel_type not in VALID_TYPES:
            raise ValueError(f"channel_type must be one of {VALID_TYPES}")

        ch = NotificationChannel(
            channel_id=channel_id, channel_type=channel_type,
            name=name, config=config or {},
        )
        self._channels[(installation_id, channel_id)] = ch
        return ch

    def test_channel(self, installation_id: str, channel_id: str, success: bool) -> NotificationChannel:
        ch = self._get(installation_id, channel_id)
        ch.test_success = success
        return ch

    def record_delivery(self, installation_id: str, channel_id: str, success: bool) -> NotificationChannel:
        ch = self._get(installation_id, channel_id)
        if success:
            ch.delivery_count += 1
        else:
            ch.failure_count += 1
        return ch

    def toggle(self, installation_id: str, channel_id: str, enabled: bool) -> NotificationChannel:
        ch = self._get(installation_id, channel_id)
        ch.enabled = enabled
        return ch

    def enabled_channels(self, installation_id: str, channel_type: str | None = None) -> list[NotificationChannel]:
        channels = [ch for (inst, _), ch in self._channels.items() if inst == installation_id and ch.enabled]
        if channel_type:
            channels = [ch for ch in channels if ch.channel_type == channel_type]
        return channels

    def list_channels(self, installation_id: str) -> list[NotificationChannel]:
        return [ch for (inst, _), ch in self._channels.items() if inst == installation_id]

    def _get(self, installation_id: str, channel_id: str) -> NotificationChannel:
        key = (installation_id, channel_id)
        ch = self._channels.get(key)
        if ch is None:
            raise KeyError(f"Channel {channel_id} not found")
        return ch

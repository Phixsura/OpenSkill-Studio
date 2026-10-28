"""App Notification Router — route app events to configured notification channels.

Routes events from installed apps to notification channels:
- Channels: webhook, email, slack, in_app
- Per-installation channel configuration
- Event type filtering per channel
- Delivery tracking with retry metadata
- Batch delivery support
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ChannelType(str, Enum):
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    IN_APP = "in_app"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChannelConfig:
    """Configuration for a notification channel."""

    channel_id: str
    channel_type: ChannelType
    target: str  # URL, email address, channel name, etc.
    event_types: list[str] | None = None  # None = all events
    enabled: bool = True


@dataclass
class NotificationEvent:
    """An event to be routed."""

    event_id: str
    event_type: str
    payload: dict
    installation_id: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class DeliveryRecord:
    """Record of a notification delivery attempt."""

    event_id: str
    channel_id: str
    installation_id: str
    status: DeliveryStatus
    timestamp: float = field(default_factory=time.time)
    error: str = ""


class AppNotificationRouter:
    """Route app events to configured notification channels."""

    def __init__(self) -> None:
        # (installation_id, channel_id) → ChannelConfig
        self._channels: dict[tuple[str, str], ChannelConfig] = {}
        # delivery records
        self._deliveries: list[DeliveryRecord] = []

    def register_channel(
        self,
        installation_id: str,
        channel_id: str,
        channel_type: ChannelType,
        target: str,
        event_types: list[str] | None = None,
    ) -> ChannelConfig:
        """Register a notification channel for an installation."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not channel_id:
            raise ValueError("channel_id is required")
        if not target:
            raise ValueError("target is required")

        config = ChannelConfig(
            channel_id=channel_id,
            channel_type=channel_type,
            target=target,
            event_types=event_types,
        )
        self._channels[(installation_id, channel_id)] = config
        log.info("notification.channel_registered",
                 channel_id=channel_id, channel_type=channel_type.value)
        return config

    def disable_channel(self, installation_id: str, channel_id: str) -> None:
        """Disable a channel without removing it."""
        config = self._get_channel(installation_id, channel_id)
        config.enabled = False

    def enable_channel(self, installation_id: str, channel_id: str) -> None:
        """Re-enable a disabled channel."""
        config = self._get_channel(installation_id, channel_id)
        config.enabled = True

    def remove_channel(self, installation_id: str, channel_id: str) -> None:
        """Remove a channel."""
        key = (installation_id, channel_id)
        if key not in self._channels:
            raise KeyError(f"Channel {channel_id} not found")
        del self._channels[key]

    def route(self, event: NotificationEvent) -> list[DeliveryRecord]:
        """Route an event to matching channels. Returns delivery records."""
        matching = self._match_channels(event.installation_id, event.event_type)
        records: list[DeliveryRecord] = []

        for config in matching:
            if not config.enabled:
                record = DeliveryRecord(
                    event_id=event.event_id,
                    channel_id=config.channel_id,
                    installation_id=event.installation_id,
                    status=DeliveryStatus.SKIPPED,
                    error="channel disabled",
                )
            else:
                # In a real system, this would call the actual channel.
                # Here we simulate successful delivery.
                record = DeliveryRecord(
                    event_id=event.event_id,
                    channel_id=config.channel_id,
                    installation_id=event.installation_id,
                    status=DeliveryStatus.DELIVERED,
                )
                log.info("notification.delivered",
                         event_id=event.event_id,
                         channel_id=config.channel_id)

            records.append(record)
            self._deliveries.append(record)

        if not matching:
            log.debug("notification.no_channels",
                      event_id=event.event_id,
                      event_type=event.event_type)

        return records

    def route_batch(self, events: list[NotificationEvent]) -> list[DeliveryRecord]:
        """Route multiple events. Returns all delivery records."""
        all_records: list[DeliveryRecord] = []
        for event in events:
            all_records.extend(self.route(event))
        return all_records

    def get_deliveries(
        self,
        installation_id: str,
        event_id: str | None = None,
        limit: int = 50,
    ) -> list[DeliveryRecord]:
        """Get delivery records for an installation, newest first."""
        if not installation_id:
            raise ValueError("installation_id is required")
        records = [r for r in self._deliveries if r.installation_id == installation_id]
        if event_id:
            records = [r for r in records if r.event_id == event_id]
        return list(reversed(records[-limit:]))

    def list_channels(self, installation_id: str) -> list[ChannelConfig]:
        """List all channels for an installation."""
        return [
            config for (inst, _), config in self._channels.items()
            if inst == installation_id
        ]

    def _match_channels(
        self, installation_id: str, event_type: str
    ) -> list[ChannelConfig]:
        """Find channels that match an event type."""
        result = []
        for (inst, _), config in self._channels.items():
            if inst != installation_id:
                continue
            # None event_types means all events
            if config.event_types is None or event_type in config.event_types:
                result.append(config)
        return result

    def _get_channel(self, installation_id: str, channel_id: str) -> ChannelConfig:
        key = (installation_id, channel_id)
        config = self._channels.get(key)
        if config is None:
            raise KeyError(f"Channel {channel_id} not found")
        return config

"""Consumer Notification Preferences — per-consumer notification channel settings."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

CHANNELS = ("email", "slack", "webhook", "sms", "in_app")
EVENT_TYPES = ("incident", "maintenance", "usage_alert", "billing", "security", "changelog")


@dataclass
class ChannelConfig:
    channel: str
    enabled: bool = True
    destination: str = ""  # email addr, webhook url, slack channel, phone


@dataclass
class NotificationPreference:
    event_type: str
    channels: dict[str, ChannelConfig] = field(default_factory=dict)
    muted: bool = False


@dataclass
class NotifPrefsManager:
    """Manage per-consumer notification preferences."""

    _prefs: dict[str, dict[str, NotificationPreference]] = field(default_factory=dict)

    def set_channel(self, consumer_id: str, event_type: str, channel: str,
                    enabled: bool = True, destination: str = "") -> dict:
        if channel not in CHANNELS:
            raise ValueError(f"Invalid channel: {channel}")
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Invalid event type: {event_type}")
        prefs = self._prefs.setdefault(consumer_id, {})
        pref = prefs.setdefault(event_type, NotificationPreference(event_type=event_type))
        pref.channels[channel] = ChannelConfig(channel=channel, enabled=enabled,
                                                destination=destination)
        logger.info("notif_pref_set", consumer_id=consumer_id,
                     event_type=event_type, channel=channel)
        return {"consumer_id": consumer_id, "event_type": event_type,
                "channel": channel, "enabled": enabled}

    def mute_event(self, consumer_id: str, event_type: str, muted: bool = True) -> dict:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Invalid event type: {event_type}")
        prefs = self._prefs.setdefault(consumer_id, {})
        pref = prefs.setdefault(event_type, NotificationPreference(event_type=event_type))
        pref.muted = muted
        return {"consumer_id": consumer_id, "event_type": event_type, "muted": muted}

    def should_notify(self, consumer_id: str, event_type: str, channel: str) -> dict:
        prefs = self._prefs.get(consumer_id, {})
        pref = prefs.get(event_type)
        if not pref:
            return {"notify": True, "reason": "no_preference_defaults_on"}
        if pref.muted:
            return {"notify": False, "reason": "event_muted"}
        ch = pref.channels.get(channel)
        if not ch:
            return {"notify": True, "reason": "channel_not_configured_defaults_on"}
        if not ch.enabled:
            return {"notify": False, "reason": "channel_disabled"}
        return {"notify": True, "reason": "enabled", "destination": ch.destination}

    def get_preferences(self, consumer_id: str) -> list[dict]:
        prefs = self._prefs.get(consumer_id, {})
        results = []
        for event_type in EVENT_TYPES:
            pref = prefs.get(event_type)
            if pref:
                channels = {ch: {"enabled": cfg.enabled, "destination": cfg.destination}
                            for ch, cfg in pref.channels.items()}
                results.append({"event_type": event_type, "muted": pref.muted,
                                "channels": channels})
            else:
                results.append({"event_type": event_type, "muted": False, "channels": {}})
        return results

    def get_active_channels(self, consumer_id: str, event_type: str) -> list[str]:
        prefs = self._prefs.get(consumer_id, {})
        pref = prefs.get(event_type)
        if not pref or pref.muted:
            return []
        return [ch for ch, cfg in pref.channels.items() if cfg.enabled]

    def reset(self, consumer_id: str) -> dict:
        removed = consumer_id in self._prefs
        self._prefs.pop(consumer_id, None)
        return {"reset": removed}

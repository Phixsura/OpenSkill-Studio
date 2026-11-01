"""App API Notification Preference — per-user notification settings.

Manages notification preferences:
- Set channel preferences per user (email, slack, in_app)
- Event type opt-in/opt-out
- Quiet hours configuration
- Per-installation scoped preferences
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class NotificationPreference:
    """A user's notification preferences."""

    user_id: str
    channels: set[str] = field(default_factory=lambda: {"email", "in_app"})
    muted_events: set[str] = field(default_factory=set)
    quiet_start: int | None = None  # hour 0-23
    quiet_end: int | None = None


VALID_CHANNELS = {"email", "slack", "in_app", "sms", "webhook"}


class AppAPINotificationPreference:
    """Per-user notification settings."""

    def __init__(self) -> None:
        self._prefs: dict[tuple[str, str], NotificationPreference] = {}

    def get_or_create(self, installation_id: str, user_id: str) -> NotificationPreference:
        key = (installation_id, user_id)
        if key not in self._prefs:
            self._prefs[key] = NotificationPreference(user_id=user_id)
        return self._prefs[key]

    def set_channels(self, installation_id: str, user_id: str, channels: list[str]) -> NotificationPreference:
        for c in channels:
            if c not in VALID_CHANNELS:
                raise ValueError(f"Invalid channel: {c}")
        pref = self.get_or_create(installation_id, user_id)
        pref.channels = set(channels)
        return pref

    def mute_event(self, installation_id: str, user_id: str, event_type: str) -> NotificationPreference:
        pref = self.get_or_create(installation_id, user_id)
        pref.muted_events.add(event_type)
        return pref

    def unmute_event(self, installation_id: str, user_id: str, event_type: str) -> NotificationPreference:
        pref = self.get_or_create(installation_id, user_id)
        pref.muted_events.discard(event_type)
        return pref

    def should_notify(self, installation_id: str, user_id: str, event_type: str, channel: str) -> bool:
        pref = self._prefs.get((installation_id, user_id))
        if pref is None:
            return True  # default: notify
        if channel not in pref.channels:
            return False
        if event_type in pref.muted_events:
            return False
        return True

    def set_quiet_hours(self, installation_id: str, user_id: str, start: int, end: int) -> NotificationPreference:
        if not (0 <= start <= 23 and 0 <= end <= 23):
            raise ValueError("hours must be 0-23")
        pref = self.get_or_create(installation_id, user_id)
        pref.quiet_start = start
        pref.quiet_end = end
        return pref

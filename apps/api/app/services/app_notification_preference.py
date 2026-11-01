"""App Notification Preference — manage per-user notification settings.

Manages notification preferences for installed apps:
- Define notification channels (email, push, in_app, sms)
- Per-user opt-in/opt-out per channel and category
- Quiet hours support
- Global mute toggle
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class NotificationPref:
    """User notification preferences."""

    user_id: str
    channels: dict[str, bool] = field(default_factory=lambda: {
        "email": True, "push": True, "in_app": True, "sms": False,
    })
    muted_categories: list[str] = field(default_factory=list)
    global_mute: bool = False
    quiet_hours_start: int | None = None  # hour 0-23
    quiet_hours_end: int | None = None


class AppNotificationPreference:
    """Manage per-user notification settings."""

    def __init__(self) -> None:
        # (installation_id, user_id) → NotificationPref
        self._prefs: dict[tuple[str, str], NotificationPref] = {}

    def get_or_create(self, installation_id: str, user_id: str) -> NotificationPref:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        key = (installation_id, user_id)
        if key not in self._prefs:
            self._prefs[key] = NotificationPref(user_id=user_id)
        return self._prefs[key]

    def set_channel(
        self, installation_id: str, user_id: str, channel: str, enabled: bool
    ) -> NotificationPref:
        pref = self.get_or_create(installation_id, user_id)
        if channel not in ("email", "push", "in_app", "sms"):
            raise ValueError(f"Invalid channel: {channel}")
        pref.channels[channel] = enabled
        return pref

    def mute_category(
        self, installation_id: str, user_id: str, category: str
    ) -> NotificationPref:
        pref = self.get_or_create(installation_id, user_id)
        if category not in pref.muted_categories:
            pref.muted_categories.append(category)
        return pref

    def unmute_category(
        self, installation_id: str, user_id: str, category: str
    ) -> NotificationPref:
        pref = self.get_or_create(installation_id, user_id)
        pref.muted_categories = [c for c in pref.muted_categories if c != category]
        return pref

    def set_global_mute(
        self, installation_id: str, user_id: str, muted: bool
    ) -> NotificationPref:
        pref = self.get_or_create(installation_id, user_id)
        pref.global_mute = muted
        return pref

    def set_quiet_hours(
        self, installation_id: str, user_id: str,
        start_hour: int, end_hour: int,
    ) -> NotificationPref:
        if not 0 <= start_hour <= 23 or not 0 <= end_hour <= 23:
            raise ValueError("Hours must be 0-23")
        pref = self.get_or_create(installation_id, user_id)
        pref.quiet_hours_start = start_hour
        pref.quiet_hours_end = end_hour
        return pref

    def should_notify(
        self, installation_id: str, user_id: str,
        channel: str, category: str = "", current_hour: int | None = None,
    ) -> bool:
        """Check if a notification should be sent."""
        key = (installation_id, user_id)
        pref = self._prefs.get(key)
        if pref is None:
            return True  # default: allow

        if pref.global_mute:
            return False
        if not pref.channels.get(channel, False):
            return False
        if category and category in pref.muted_categories:
            return False
        if (current_hour is not None and pref.quiet_hours_start is not None
                and pref.quiet_hours_end is not None):
            if pref.quiet_hours_start <= pref.quiet_hours_end:
                if pref.quiet_hours_start <= current_hour < pref.quiet_hours_end:
                    return False
            else:  # wraps midnight
                if current_hour >= pref.quiet_hours_start or current_hour < pref.quiet_hours_end:
                    return False
        return True

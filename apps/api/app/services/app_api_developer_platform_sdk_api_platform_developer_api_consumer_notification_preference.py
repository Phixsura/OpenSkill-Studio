"""API Consumer Notification Preference — manage per-consumer notification settings."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class NotificationPreference:
    consumer_id: str
    email_enabled: bool = True
    slack_enabled: bool = False
    webhook_enabled: bool = True
    channels: dict[str, bool] = field(default_factory=dict)  # event_type → enabled
    frequency: str = "realtime"  # "realtime", "hourly", "daily"
    quiet_hours_start: int = -1  # -1 = disabled, 0-23 = hour
    quiet_hours_end: int = -1

VALID_FREQUENCIES = {"realtime", "hourly", "daily", "weekly"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreference:
    def __init__(self) -> None:
        self._prefs: dict[tuple[str, str], NotificationPreference] = {}

    def set_preference(self, installation_id: str, pref: NotificationPreference) -> NotificationPreference:
        if not installation_id: raise ValueError("installation_id is required")
        if pref.frequency not in VALID_FREQUENCIES: raise ValueError(f"Invalid frequency: {pref.frequency}")
        if pref.quiet_hours_start != -1 and not 0 <= pref.quiet_hours_start <= 23:
            raise ValueError("quiet_hours_start must be 0-23 or -1")
        self._prefs[(installation_id, pref.consumer_id)] = pref
        return pref

    def should_notify(self, installation_id: str, consumer_id: str, event_type: str, current_hour: int = -1) -> bool:
        pref = self._prefs.get((installation_id, consumer_id))
        if pref is None: return True  # default: notify
        # Check quiet hours
        if pref.quiet_hours_start != -1 and current_hour != -1:
            if pref.quiet_hours_start <= pref.quiet_hours_end:
                if pref.quiet_hours_start <= current_hour < pref.quiet_hours_end: return False
            else:  # wraps midnight
                if current_hour >= pref.quiet_hours_start or current_hour < pref.quiet_hours_end: return False
        # Check channel opt-out
        if event_type in pref.channels: return pref.channels[event_type]
        return True

    def get_preference(self, installation_id: str, consumer_id: str) -> NotificationPreference | None:
        return self._prefs.get((installation_id, consumer_id))

    def list_preferences(self, installation_id: str) -> list[NotificationPreference]:
        return [p for (inst, _), p in self._prefs.items() if inst == installation_id]

    def consumer_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._prefs if inst == installation_id)

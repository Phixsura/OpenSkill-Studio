"""Developer Notification Preferences — per-channel, per-event notification settings."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class NotifPrefs:
    user_id: str
    channels: dict[str, bool] = field(default_factory=lambda: {
        "email": True, "in_app": True, "webhook": False, "slack": False,
    })
    events: dict[str, bool] = field(default_factory=lambda: {
        "install": True, "uninstall": True, "review": True,
        "update": True, "security": True, "revenue": True,
    })
    quiet_hours: tuple[int, int] = (0, 0)  # start_hour, end_hour (0=disabled)


class DevNotifPrefsService:
    def __init__(self):
        self._prefs: dict[str, NotifPrefs] = {}

    def get_or_create(self, user_id: str) -> NotifPrefs:
        if user_id not in self._prefs:
            self._prefs[user_id] = NotifPrefs(user_id=user_id)
        return self._prefs[user_id]

    def set_channel(self, user_id: str, channel: str, enabled: bool) -> bool:
        p = self.get_or_create(user_id)
        if channel not in p.channels:
            return False
        p.channels[channel] = enabled
        return True

    def set_event(self, user_id: str, event: str, enabled: bool) -> bool:
        p = self.get_or_create(user_id)
        if event not in p.events:
            return False
        p.events[event] = enabled
        return True

    def set_quiet_hours(self, user_id: str, start: int, end: int) -> bool:
        if not (0 <= start <= 23 and 0 <= end <= 23):
            return False
        p = self.get_or_create(user_id)
        p.quiet_hours = (start, end)
        return True

    def should_notify(self, user_id: str, event: str, channel: str, hour: int = 12) -> bool:
        p = self.get_or_create(user_id)
        if not p.channels.get(channel, False):
            return False
        if not p.events.get(event, False):
            return False
        s, e = p.quiet_hours
        if s != e:  # quiet hours enabled
            if s < e and s <= hour < e:
                return False
            if s > e and (hour >= s or hour < e):
                return False
        return True

"""Notification Preferences — fine-grained notification controls per event type.

Manages per-event notification preferences with channel selection,
quiet hours, digest mode, and do-not-disturb.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class NotifPreference:
    event_type: str
    email: bool = True
    in_app: bool = True
    push: bool = False
    webhook: bool = False
    digest: bool = False  # batch into daily digest


@dataclass
class QuietHours:
    enabled: bool = False
    start_hour: int = 22  # 10 PM
    end_hour: int = 8     # 8 AM
    timezone: str = "UTC"


class ExtensionNotifPreferencesService:
    """Per-event notification preferences with quiet hours."""

    DEFAULT_EVENTS = [
        "deploy.success", "deploy.failed", "review.submitted", "review.approved",
        "install.new", "uninstall", "error.critical", "billing.invoice",
        "security.alert", "update.available",
    ]

    def __init__(self):
        self._prefs: dict[str, dict[str, NotifPreference]] = defaultdict(dict)
        self._quiet: dict[str, QuietHours] = {}
        self._dnd: set[str] = set()

    def initialize(self, user_id: str) -> list[NotifPreference]:
        prefs = []
        for event in self.DEFAULT_EVENTS:
            p = NotifPreference(event_type=event)
            if "critical" in event or "security" in event:
                p.push = True  # critical events get push by default
            self._prefs[user_id][event] = p
            prefs.append(p)
        return prefs

    def update(self, user_id: str, event_type: str, **channels: bool) -> NotifPreference | None:
        pref = self._prefs.get(user_id, {}).get(event_type)
        if not pref:
            return None
        for channel, enabled in channels.items():
            if hasattr(pref, channel):
                setattr(pref, channel, enabled)
        return pref

    def set_quiet_hours(self, user_id: str, enabled: bool,
                        start: int = 22, end: int = 8) -> QuietHours:
        qh = QuietHours(enabled=enabled, start_hour=start, end_hour=end)
        self._quiet[user_id] = qh
        return qh

    def toggle_dnd(self, user_id: str) -> bool:
        if user_id in self._dnd:
            self._dnd.discard(user_id)
            return False
        self._dnd.add(user_id)
        return True

    def is_dnd(self, user_id: str) -> bool:
        return user_id in self._dnd

    def should_notify(self, user_id: str, event_type: str, channel: str) -> bool:
        if self.is_dnd(user_id):
            return False
        pref = self._prefs.get(user_id, {}).get(event_type)
        if not pref:
            return True  # default: notify
        return getattr(pref, channel, False)

    def get_preferences(self, user_id: str) -> list[NotifPreference]:
        return list(self._prefs.get(user_id, {}).values())

    def get_summary(self, user_id: str) -> dict:
        prefs = self._prefs.get(user_id, {})
        return {
            "total_events": len(prefs),
            "email_enabled": sum(1 for p in prefs.values() if p.email),
            "push_enabled": sum(1 for p in prefs.values() if p.push),
            "dnd": self.is_dnd(user_id),
            "quiet_hours": self._quiet.get(user_id, QuietHours()).enabled,
        }

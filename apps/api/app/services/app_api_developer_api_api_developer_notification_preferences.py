"""App API Developer Notification Preferences — per-developer notification settings."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

CHANNELS = {"email", "slack", "webhook", "in_app"}
CATEGORIES = {"incident", "deprecation", "changelog", "usage_alert", "security", "billing"}

@dataclass
class NotificationPreference:
    developer_id: str
    enabled_channels: set[str] = field(default_factory=lambda: {"email", "in_app"})
    enabled_categories: set[str] = field(default_factory=lambda: set(CATEGORIES))
    quiet_hours_start: int | None = None  # hour 0-23
    quiet_hours_end: int | None = None

class AppAPIDeveloperAPIApiDeveloperNotificationPreferences:
    def __init__(self) -> None:
        self._prefs: dict[tuple[str, str], NotificationPreference] = {}

    def get_or_create(self, installation_id: str, developer_id: str) -> NotificationPreference:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, developer_id)
        if key not in self._prefs:
            self._prefs[key] = NotificationPreference(developer_id=developer_id)
        return self._prefs[key]

    def set_channels(self, installation_id: str, developer_id: str, channels: list[str]) -> NotificationPreference:
        invalid = set(channels) - CHANNELS
        if invalid: raise ValueError(f"Invalid channels: {invalid}")
        p = self.get_or_create(installation_id, developer_id)
        p.enabled_channels = set(channels)
        return p

    def set_categories(self, installation_id: str, developer_id: str, categories: list[str]) -> NotificationPreference:
        invalid = set(categories) - CATEGORIES
        if invalid: raise ValueError(f"Invalid categories: {invalid}")
        p = self.get_or_create(installation_id, developer_id)
        p.enabled_categories = set(categories)
        return p

    def should_notify(self, installation_id: str, developer_id: str, category: str, channel: str) -> bool:
        p = self.get_or_create(installation_id, developer_id)
        return category in p.enabled_categories and channel in p.enabled_channels

    def set_quiet_hours(self, installation_id: str, developer_id: str, start: int, end: int) -> NotificationPreference:
        if not 0 <= start <= 23 or not 0 <= end <= 23: raise ValueError("hours must be 0-23")
        p = self.get_or_create(installation_id, developer_id)
        p.quiet_hours_start = start
        p.quiet_hours_end = end
        return p

"""Consumer Notification Preference — manage how consumers receive platform notifications."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class NotificationChannel:
    channel_type: str  # "email", "webhook", "slack", "in_app"
    target: str        # email address, URL, channel ID
    enabled: bool = True

@dataclass
class NotificationPreference:
    consumer_id: str
    channels: list[NotificationChannel] = field(default_factory=list)
    muted_categories: set[str] = field(default_factory=set)  # e.g. {"billing", "maintenance"}
    digest_mode: str = "instant"  # "instant", "hourly", "daily"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreference:
    def __init__(self) -> None:
        self._prefs: dict[tuple[str, str], NotificationPreference] = {}

    def set_preference(self, installation_id: str, pref: NotificationPreference) -> NotificationPreference:
        if not installation_id:
            raise ValueError("installation_id is required")
        if pref.digest_mode not in ("instant", "hourly", "daily"):
            raise ValueError(f"Invalid digest_mode: {pref.digest_mode}")
        self._prefs[(installation_id, pref.consumer_id)] = pref
        log.info("notification_pref_set", installation_id=installation_id, consumer_id=pref.consumer_id, channels=len(pref.channels))
        return pref

    def get_preference(self, installation_id: str, consumer_id: str) -> NotificationPreference | None:
        return self._prefs.get((installation_id, consumer_id))

    def should_notify(self, installation_id: str, consumer_id: str, category: str) -> list[NotificationChannel]:
        pref = self._prefs.get((installation_id, consumer_id))
        if not pref:
            return []
        if category in pref.muted_categories:
            return []
        return [ch for ch in pref.channels if ch.enabled]

    def mute(self, installation_id: str, consumer_id: str, category: str) -> NotificationPreference:
        pref = self._prefs.get((installation_id, consumer_id))
        if not pref:
            raise ValueError("Preference not found")
        pref.muted_categories.add(category)
        return pref

    def unmute(self, installation_id: str, consumer_id: str, category: str) -> NotificationPreference:
        pref = self._prefs.get((installation_id, consumer_id))
        if not pref:
            raise ValueError("Preference not found")
        pref.muted_categories.discard(category)
        return pref

    def list_preferences(self, installation_id: str) -> list[NotificationPreference]:
        return [p for (inst, _), p in self._prefs.items() if inst == installation_id]

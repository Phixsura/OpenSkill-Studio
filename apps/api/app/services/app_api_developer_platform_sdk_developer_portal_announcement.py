"""App API Developer Portal Announcement — manage platform announcements."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class Announcement:
    announcement_id: str
    title: str
    body: str
    severity: str  # "info", "warning", "critical", "maintenance"
    active: bool = True
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    views: int = 0

    @property
    def expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class AppAPIDeveloperPlatformSDKDeveloperPortalAnnouncement:
    def __init__(self) -> None:
        self._announcements: dict[tuple[str, str], Announcement] = {}

    def create(self, installation_id: str, announcement_id: str, title: str, body: str, severity: str, expires_at: float | None = None) -> Announcement:
        if not installation_id: raise ValueError("installation_id is required")
        if severity not in ("info", "warning", "critical", "maintenance"): raise ValueError("invalid severity")
        key = (installation_id, announcement_id)
        if key in self._announcements: raise ValueError(f"Announcement {announcement_id} exists")
        a = Announcement(announcement_id=announcement_id, title=title, body=body, severity=severity, expires_at=expires_at)
        self._announcements[key] = a
        return a

    def view(self, installation_id: str, announcement_id: str) -> Announcement:
        key = (installation_id, announcement_id)
        a = self._announcements.get(key)
        if a is None: raise KeyError(f"Announcement {announcement_id} not found")
        a.views += 1
        return a

    def dismiss(self, installation_id: str, announcement_id: str) -> Announcement:
        key = (installation_id, announcement_id)
        a = self._announcements.get(key)
        if a is None: raise KeyError(f"Announcement {announcement_id} not found")
        a.active = False
        return a

    def active_announcements(self, installation_id: str) -> list[Announcement]:
        return [a for (inst, _), a in self._announcements.items() if inst == installation_id and a.active and not a.expired]

    def all_announcements(self, installation_id: str) -> list[Announcement]:
        return [a for (inst, _), a in self._announcements.items() if inst == installation_id]

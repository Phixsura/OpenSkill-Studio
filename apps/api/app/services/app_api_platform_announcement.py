"""App API Platform Announcement — broadcast platform-wide announcements."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class Announcement:
    announcement_id: str
    title: str
    body: str
    severity: str  # "info", "warning", "critical"
    active: bool = True
    created_at: float = field(default_factory=time.time)

VALID_SEVERITY = {"info", "warning", "critical"}

class AppAPIPlatformAnnouncement:
    def __init__(self) -> None:
        self._announcements: dict[tuple[str, str], Announcement] = {}

    def create(self, installation_id: str, announcement_id: str, title: str, body: str, severity: str = "info") -> Announcement:
        if not installation_id: raise ValueError("installation_id is required")
        if severity not in VALID_SEVERITY: raise ValueError(f"severity must be one of {VALID_SEVERITY}")
        key = (installation_id, announcement_id)
        if key in self._announcements: raise ValueError(f"Announcement {announcement_id} exists")
        a = Announcement(announcement_id=announcement_id, title=title, body=body, severity=severity)
        self._announcements[key] = a
        return a

    def dismiss(self, installation_id: str, announcement_id: str) -> Announcement:
        a = self._get(installation_id, announcement_id)
        a.active = False
        return a

    def active_announcements(self, installation_id: str) -> list[Announcement]:
        return [a for (inst, _), a in self._announcements.items() if inst == installation_id and a.active]

    def list_all(self, installation_id: str) -> list[Announcement]:
        return [a for (inst, _), a in self._announcements.items() if inst == installation_id]

    def _get(self, installation_id: str, announcement_id: str) -> Announcement:
        a = self._announcements.get((installation_id, announcement_id))
        if a is None: raise KeyError(f"Announcement {announcement_id} not found")
        return a

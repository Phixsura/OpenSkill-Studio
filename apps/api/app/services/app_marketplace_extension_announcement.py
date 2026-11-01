"""Announcement System — platform-wide announcements for developers.

Manages announcements with targeting, scheduling, dismissal tracking,
priority levels, and audience segmentation.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class AnnouncementType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    FEATURE = "feature"
    MAINTENANCE = "maintenance"


@dataclass
class Announcement:
    announcement_id: str
    title: str
    body: str
    ann_type: AnnouncementType
    priority: int = 0
    target_audience: str = "all"  # all, developers, admins
    active: bool = True
    dismissible: bool = True
    created_at: float = 0.0
    expires_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    @property
    def expired(self) -> bool:
        return self.expires_at > 0 and time.time() > self.expires_at


class ExtensionAnnouncementService:
    """Manages platform announcements with targeting."""

    def __init__(self):
        self._announcements: list[Announcement] = []
        self._dismissed: dict[str, set[str]] = {}  # user_id -> {announcement_ids}

    def create(self, title: str, body: str,
               ann_type: AnnouncementType = AnnouncementType.INFO,
               priority: int = 0, target: str = "all",
               dismissible: bool = True, expires_in: float = 0) -> Announcement:
        ann = Announcement(
            announcement_id=f"ann_{secrets.token_urlsafe(8)}",
            title=title, body=body, ann_type=ann_type,
            priority=priority, target_audience=target,
            dismissible=dismissible,
            expires_at=time.time() + expires_in if expires_in != 0 else 0,
        )
        self._announcements.append(ann)
        return ann

    def get_active(self, user_id: str, audience: str = "all") -> list[Announcement]:
        dismissed = self._dismissed.get(user_id, set())
        return [a for a in self._announcements
                if a.active and not a.expired
                and a.announcement_id not in dismissed
                and (a.target_audience == "all" or a.target_audience == audience)]

    def dismiss(self, user_id: str, announcement_id: str) -> bool:
        ann = next((a for a in self._announcements if a.announcement_id == announcement_id), None)
        if not ann or not ann.dismissible:
            return False
        self._dismissed.setdefault(user_id, set()).add(announcement_id)
        return True

    def deactivate(self, announcement_id: str) -> bool:
        ann = next((a for a in self._announcements if a.announcement_id == announcement_id), None)
        if ann:
            ann.active = False
            return True
        return False

    def get_all(self) -> list[Announcement]:
        return list(self._announcements)

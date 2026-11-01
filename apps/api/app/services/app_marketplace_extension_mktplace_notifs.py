"""Marketplace Notifications — centralized notification system."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque


@dataclass
class Notification:
    notif_id: str
    user_id: str
    title: str
    body: str
    category: str  # install, update, review, security, system, revenue
    read: bool = False
    action_url: str = ""
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class MktplaceNotifsService:
    MAX_PER_USER = 500

    def __init__(self):
        self._notifications: dict[str, deque[Notification]] = {}
        self._counter = 0

    def send(self, user_id: str, title: str, body: str, category: str,
             action_url: str = "") -> Notification:
        self._counter += 1
        notif = Notification(notif_id=f"notif-{self._counter}", user_id=user_id,
                             title=title, body=body, category=category,
                             action_url=action_url)
        if user_id not in self._notifications:
            self._notifications[user_id] = deque(maxlen=self.MAX_PER_USER)
        self._notifications[user_id].append(notif)
        return notif

    def get_unread(self, user_id: str) -> list[Notification]:
        return [n for n in self._notifications.get(user_id, []) if not n.read]

    def mark_read(self, user_id: str, notif_id: str) -> bool:
        for n in self._notifications.get(user_id, []):
            if n.notif_id == notif_id:
                n.read = True
                return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        count = 0
        for n in self._notifications.get(user_id, []):
            if not n.read:
                n.read = True
                count += 1
        return count

    def get_by_category(self, user_id: str, category: str) -> list[Notification]:
        return [n for n in self._notifications.get(user_id, []) if n.category == category]

    def get_unread_count(self, user_id: str) -> int:
        return len(self.get_unread(user_id))

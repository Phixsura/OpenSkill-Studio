"""Sandbox Notification Queue — queue and deliver notifications to extension users.

Manages notification delivery with priority, read/unread tracking,
batching, deduplication, and retention policies.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


PRIORITY_ORDER = {NotificationPriority.LOW: 0, NotificationPriority.NORMAL: 1,
                  NotificationPriority.HIGH: 2, NotificationPriority.URGENT: 3}


@dataclass
class Notification:
    notification_id: str
    sandbox_id: str
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    category: str = ""
    read: bool = False
    delivered: bool = False
    dedup_key: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class SandboxNotificationQueueService:
    """Manages notification queue with priority and deduplication."""

    MAX_NOTIFICATIONS = 500
    RETENTION_HOURS = 72

    def __init__(self):
        self._queue: dict[str, list[Notification]] = defaultdict(list)
        self._dedup_keys: dict[str, set[str]] = defaultdict(set)

    def send(self, sandbox_id: str, title: str, message: str,
             priority: NotificationPriority = NotificationPriority.NORMAL,
             category: str = "", dedup_key: str = "") -> Notification | None:
        # Deduplication
        if dedup_key:
            if dedup_key in self._dedup_keys[sandbox_id]:
                return None  # duplicate suppressed
            self._dedup_keys[sandbox_id].add(dedup_key)

        notification = Notification(
            notification_id=f"ntf_{secrets.token_urlsafe(8)}",
            sandbox_id=sandbox_id, title=title, message=message,
            priority=priority, category=category, dedup_key=dedup_key,
        )

        queue = self._queue[sandbox_id]
        queue.append(notification)
        if len(queue) > self.MAX_NOTIFICATIONS:
            self._queue[sandbox_id] = queue[-self.MAX_NOTIFICATIONS:]

        return notification

    def get_unread(self, sandbox_id: str, limit: int = 50) -> list[Notification]:
        queue = self._queue.get(sandbox_id, [])
        unread = [n for n in queue if not n.read]
        unread.sort(key=lambda n: PRIORITY_ORDER.get(n.priority, 0), reverse=True)
        return unread[:limit]

    def mark_read(self, sandbox_id: str, notification_id: str) -> bool:
        for n in self._queue.get(sandbox_id, []):
            if n.notification_id == notification_id:
                n.read = True
                return True
        return False

    def mark_all_read(self, sandbox_id: str) -> int:
        count = 0
        for n in self._queue.get(sandbox_id, []):
            if not n.read:
                n.read = True
                count += 1
        return count

    def get_by_category(self, sandbox_id: str, category: str) -> list[Notification]:
        return [n for n in self._queue.get(sandbox_id, []) if n.category == category]

    def get_unread_count(self, sandbox_id: str) -> dict:
        queue = self._queue.get(sandbox_id, [])
        unread = [n for n in queue if not n.read]
        by_priority: dict[str, int] = defaultdict(int)
        for n in unread:
            by_priority[n.priority.value] += 1
        return {"total": len(unread), "by_priority": dict(by_priority)}

    def delete(self, sandbox_id: str, notification_id: str) -> bool:
        queue = self._queue.get(sandbox_id, [])
        for i, n in enumerate(queue):
            if n.notification_id == notification_id:
                queue.pop(i)
                return True
        return False

    def clear(self, sandbox_id: str) -> int:
        count = len(self._queue.get(sandbox_id, []))
        self._queue[sandbox_id] = []
        self._dedup_keys[sandbox_id] = set()
        return count

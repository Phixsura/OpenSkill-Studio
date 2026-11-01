"""Content Moderation Queue — review and moderate user-generated content."""
from __future__ import annotations
from dataclasses import dataclass
import time


@dataclass
class ModerationItem:
    item_id: str
    content_type: str  # review, reply, description, screenshot
    content: str
    author_id: str
    extension_id: str
    status: str = "pending"  # pending, approved, rejected, escalated
    reviewer_id: str = ""
    reason: str = ""
    created_at: float = 0.0
    reviewed_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ContentModQueueService:
    FLAGGED_WORDS = {"spam", "scam", "hack", "exploit"}

    def __init__(self):
        self._queue: dict[str, ModerationItem] = {}
        self._counter = 0

    def submit(self, content_type: str, content: str, author_id: str,
               extension_id: str) -> ModerationItem:
        self._counter += 1
        mid = f"mod-{self._counter}"
        item = ModerationItem(item_id=mid, content_type=content_type,
                              content=content, author_id=author_id,
                              extension_id=extension_id)
        # Auto-flag suspicious content
        if any(w in content.lower() for w in self.FLAGGED_WORDS):
            item.status = "escalated"
        self._queue[mid] = item
        return item

    def review(self, item_id: str, reviewer_id: str, action: str,
               reason: str = "") -> bool:
        item = self._queue.get(item_id)
        if not item or item.status not in ("pending", "escalated"):
            return False
        if action not in ("approved", "rejected"):
            return False
        item.status = action
        item.reviewer_id = reviewer_id
        item.reason = reason
        item.reviewed_at = time.time()
        return True

    def get_pending(self, limit: int = 50) -> list[ModerationItem]:
        items = [i for i in self._queue.values() if i.status in ("pending", "escalated")]
        return sorted(items, key=lambda i: (i.status == "escalated", i.created_at), reverse=True)[:limit]

    def get_stats(self) -> dict[str, int]:
        stats: dict[str, int] = {}
        for item in self._queue.values():
            stats[item.status] = stats.get(item.status, 0) + 1
        return stats

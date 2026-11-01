"""Review Reply Manager — developers reply to user reviews."""
from __future__ import annotations
from dataclasses import dataclass
import time


@dataclass
class ReviewReply:
    reply_id: str
    review_id: str
    developer_id: str
    content: str
    created_at: float = 0.0
    edited_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ReviewReplyMgrService:
    def __init__(self):
        self._replies: dict[str, ReviewReply] = {}  # key: review_id
        self._counter = 0

    def reply(self, review_id: str, developer_id: str, content: str) -> ReviewReply:
        if not content.strip():
            raise ValueError("Reply cannot be empty")
        if len(content) > 2000:
            raise ValueError("Reply too long (max 2000 chars)")
        if review_id in self._replies:
            raise ValueError("Already replied to this review")
        self._counter += 1
        r = ReviewReply(reply_id=f"rr-{self._counter}", review_id=review_id,
                        developer_id=developer_id, content=content.strip())
        self._replies[review_id] = r
        return r

    def edit(self, review_id: str, developer_id: str, content: str) -> bool:
        r = self._replies.get(review_id)
        if not r or r.developer_id != developer_id:
            return False
        if not content.strip() or len(content) > 2000:
            return False
        r.content = content.strip()
        r.edited_at = time.time()
        return True

    def delete(self, review_id: str, developer_id: str) -> bool:
        r = self._replies.get(review_id)
        if r and r.developer_id == developer_id:
            del self._replies[review_id]
            return True
        return False

    def get(self, review_id: str) -> ReviewReply | None:
        return self._replies.get(review_id)

    def get_by_developer(self, developer_id: str) -> list[ReviewReply]:
        return [r for r in self._replies.values() if r.developer_id == developer_id]

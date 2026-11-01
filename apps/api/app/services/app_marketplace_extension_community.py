"""Developer Community — forum-like discussions for extension developers.

Manages discussion threads, replies, upvotes, tags, and provides
trending topics and unanswered question tracking.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Thread:
    thread_id: str
    title: str
    body: str
    author: str
    tags: list[str] = field(default_factory=list)
    reply_count: int = 0
    upvotes: int = 0
    answered: bool = False
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class ExtensionCommunityService:
    """Developer community with discussions and voting."""

    def __init__(self):
        self._threads: dict[str, Thread] = {}

    def create_thread(self, title: str, body: str, author: str,
                      tags: list[str] | None = None) -> Thread:
        thread = Thread(
            thread_id=f"thr_{secrets.token_urlsafe(8)}",
            title=title, body=body, author=author, tags=tags or [],
        )
        self._threads[thread.thread_id] = thread
        return thread

    def reply(self, thread_id: str) -> bool:
        t = self._threads.get(thread_id)
        if t:
            t.reply_count += 1
            return True
        return False

    def upvote(self, thread_id: str) -> int:
        t = self._threads.get(thread_id)
        if t:
            t.upvotes += 1
            return t.upvotes
        return 0

    def mark_answered(self, thread_id: str) -> bool:
        t = self._threads.get(thread_id)
        if t:
            t.answered = True
            return True
        return False

    def get_trending(self, limit: int = 10) -> list[Thread]:
        return sorted(self._threads.values(),
                      key=lambda t: t.upvotes + t.reply_count * 2, reverse=True)[:limit]

    def get_unanswered(self, limit: int = 10) -> list[Thread]:
        return [t for t in self._threads.values() if not t.answered][:limit]

    def search(self, query: str) -> list[Thread]:
        q = query.lower()
        return [t for t in self._threads.values()
                if q in t.title.lower() or q in t.body.lower()
                or any(q in tag for tag in t.tags)]

    def get_by_tag(self, tag: str) -> list[Thread]:
        return [t for t in self._threads.values() if tag in t.tags]

    def get_stats(self) -> dict:
        threads = list(self._threads.values())
        return {
            "total_threads": len(threads),
            "answered": sum(1 for t in threads if t.answered),
            "unanswered": sum(1 for t in threads if not t.answered),
            "total_upvotes": sum(t.upvotes for t in threads),
            "total_replies": sum(t.reply_count for t in threads),
        }

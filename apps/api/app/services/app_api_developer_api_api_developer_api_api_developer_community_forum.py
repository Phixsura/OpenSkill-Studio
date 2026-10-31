"""App API Developer Community Forum — developer community discussion management."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ForumPost:
    post_id: str
    author_id: str
    title: str
    category: str  # "question", "discussion", "announcement", "showcase", "bug_report"
    status: str = "open"  # "open", "answered", "closed"
    reply_count: int = 0
    upvotes: int = 0
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForum:
    def __init__(self) -> None:
        self._posts: dict[tuple[str, str], ForumPost] = {}

    def create_post(self, installation_id: str, post_id: str, author_id: str, title: str, category: str) -> ForumPost:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"question", "discussion", "announcement", "showcase", "bug_report"}
        if category not in valid: raise ValueError("invalid category")
        key = (installation_id, post_id)
        if key in self._posts: raise ValueError(f"Post {post_id} exists")
        p = ForumPost(post_id=post_id, author_id=author_id, title=title, category=category)
        self._posts[key] = p
        return p

    def reply(self, installation_id: str, post_id: str) -> ForumPost:
        p = self._get(installation_id, post_id)
        p.reply_count += 1
        return p

    def upvote(self, installation_id: str, post_id: str) -> ForumPost:
        p = self._get(installation_id, post_id)
        p.upvotes += 1
        return p

    def mark_answered(self, installation_id: str, post_id: str) -> ForumPost:
        p = self._get(installation_id, post_id)
        p.status = "answered"
        return p

    def trending(self, installation_id: str, limit: int = 10) -> list[ForumPost]:
        posts = [p for (inst, _), p in self._posts.items() if inst == installation_id and p.status != "closed"]
        return sorted(posts, key=lambda p: p.upvotes + p.reply_count * 2, reverse=True)[:limit]

    def unanswered(self, installation_id: str) -> list[ForumPost]:
        return [p for (inst, _), p in self._posts.items() if inst == installation_id and p.category == "question" and p.status == "open"]

    def by_category(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), p in self._posts.items():
            if inst == installation_id: counts[p.category] = counts.get(p.category, 0) + 1
        return counts

    def _get(self, installation_id: str, post_id: str) -> ForumPost:
        key = (installation_id, post_id)
        p = self._posts.get(key)
        if p is None: raise KeyError(f"Post {post_id} not found")
        return p

"""App API Developer Community — community forum and discussion management."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class Discussion:
    discussion_id: str
    title: str
    author: str
    reply_count: int = 0
    resolved: bool = False
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperCommunity:
    def __init__(self) -> None:
        self._discussions: dict[tuple[str, str], Discussion] = {}

    def create_discussion(self, installation_id: str, discussion_id: str, title: str, author: str) -> Discussion:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, discussion_id)
        if key in self._discussions: raise ValueError(f"Discussion {discussion_id} exists")
        d = Discussion(discussion_id=discussion_id, title=title, author=author)
        self._discussions[key] = d
        return d

    def add_reply(self, installation_id: str, discussion_id: str) -> Discussion:
        d = self._get(installation_id, discussion_id)
        d.reply_count += 1
        return d

    def resolve(self, installation_id: str, discussion_id: str) -> Discussion:
        d = self._get(installation_id, discussion_id)
        d.resolved = True
        return d

    def open_discussions(self, installation_id: str) -> list[Discussion]:
        return [d for (inst, _), d in self._discussions.items() if inst == installation_id and not d.resolved]

    def list_discussions(self, installation_id: str) -> list[Discussion]:
        return [d for (inst, _), d in self._discussions.items() if inst == installation_id]

    def _get(self, installation_id: str, discussion_id: str) -> Discussion:
        d = self._discussions.get((installation_id, discussion_id))
        if d is None: raise KeyError(f"Discussion {discussion_id} not found")
        return d

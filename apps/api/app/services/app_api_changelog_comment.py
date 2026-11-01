"""App API Changelog Comment — threaded comments on changelog entries.

Manages changelog comments:
- Add comments on changelog entries
- Reply threading
- Comment moderation
- Per-installation scoped comments
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ChangelogComment:
    """A comment on a changelog entry."""

    comment_id: str
    entry_id: str
    author: str
    body: str
    parent_id: str | None = None
    created_at: float = field(default_factory=time.time)
    hidden: bool = False


class AppAPIChangelogComment:
    """Threaded comments on changelog entries."""

    def __init__(self) -> None:
        self._comments: dict[str, list[ChangelogComment]] = {}

    def add_comment(
        self, installation_id: str, comment_id: str, entry_id: str,
        author: str, body: str, parent_id: str | None = None,
    ) -> ChangelogComment:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not body.strip():
            raise ValueError("body cannot be empty")

        comment = ChangelogComment(
            comment_id=comment_id, entry_id=entry_id,
            author=author, body=body, parent_id=parent_id,
        )
        self._comments.setdefault(installation_id, []).append(comment)
        return comment

    def hide_comment(self, installation_id: str, comment_id: str) -> ChangelogComment:
        for c in self._comments.get(installation_id, []):
            if c.comment_id == comment_id:
                c.hidden = True
                return c
        raise KeyError(f"Comment {comment_id} not found")

    def comments_for_entry(self, installation_id: str, entry_id: str) -> list[ChangelogComment]:
        return [c for c in self._comments.get(installation_id, []) if c.entry_id == entry_id and not c.hidden]

    def replies(self, installation_id: str, parent_id: str) -> list[ChangelogComment]:
        return [c for c in self._comments.get(installation_id, []) if c.parent_id == parent_id and not c.hidden]

    def count(self, installation_id: str, entry_id: str) -> int:
        return len(self.comments_for_entry(installation_id, entry_id))

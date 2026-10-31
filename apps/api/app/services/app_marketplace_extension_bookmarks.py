"""Extension Bookmarks — save and organize favorite extensions.

Allows developers to bookmark extensions with tags, collections,
notes, and quick access.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Bookmark:
    extension_id: str
    user_id: str
    collection: str = "default"
    note: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class ExtensionBookmarksService:
    """Manages extension bookmarks with collections and tags."""

    def __init__(self):
        self._bookmarks: dict[str, list[Bookmark]] = defaultdict(list)

    def add(self, user_id: str, extension_id: str, collection: str = "default",
            note: str = "", tags: list[str] | None = None) -> Bookmark:
        # Prevent duplicate
        for b in self._bookmarks[user_id]:
            if b.extension_id == extension_id:
                return b
        bm = Bookmark(extension_id=extension_id, user_id=user_id,
                      collection=collection, note=note, tags=tags or [])
        self._bookmarks[user_id].append(bm)
        return bm

    def remove(self, user_id: str, extension_id: str) -> bool:
        bms = self._bookmarks.get(user_id, [])
        for i, b in enumerate(bms):
            if b.extension_id == extension_id:
                bms.pop(i)
                return True
        return False

    def is_bookmarked(self, user_id: str, extension_id: str) -> bool:
        return any(b.extension_id == extension_id for b in self._bookmarks.get(user_id, []))

    def get_all(self, user_id: str, collection: str | None = None) -> list[Bookmark]:
        bms = self._bookmarks.get(user_id, [])
        if collection:
            bms = [b for b in bms if b.collection == collection]
        return bms

    def get_collections(self, user_id: str) -> list[str]:
        return sorted({b.collection for b in self._bookmarks.get(user_id, [])})

    def search(self, user_id: str, query: str) -> list[Bookmark]:
        q = query.lower()
        return [b for b in self._bookmarks.get(user_id, [])
                if q in b.extension_id.lower() or q in b.note.lower()
                or any(q in t for t in b.tags)]

    def get_count(self, user_id: str) -> int:
        return len(self._bookmarks.get(user_id, []))

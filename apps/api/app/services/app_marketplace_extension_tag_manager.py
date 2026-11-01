"""Extension Tag Manager — manage tags for extensions."""
from __future__ import annotations
from collections import defaultdict

class ExtensionTagManagerService:
    def __init__(self):
        self._tags: dict[str, set[str]] = defaultdict(set)

    def add_tags(self, extension_id: str, tags: list[str]) -> list[str]:
        self._tags[extension_id].update(tags)
        return sorted(self._tags[extension_id])

    def remove_tag(self, extension_id: str, tag: str) -> bool:
        if tag in self._tags.get(extension_id, set()):
            self._tags[extension_id].discard(tag)
            return True
        return False

    def get_tags(self, extension_id: str) -> list[str]:
        return sorted(self._tags.get(extension_id, set()))

    def find_by_tag(self, tag: str) -> list[str]:
        return sorted(eid for eid, tags in self._tags.items() if tag in tags)

    def get_popular_tags(self, limit: int = 20) -> list[tuple[str, int]]:
        counts: dict[str, int] = defaultdict(int)
        for tags in self._tags.values():
            for t in tags:
                counts[t] += 1
        return sorted(counts.items(), key=lambda x: -x[1])[:limit]

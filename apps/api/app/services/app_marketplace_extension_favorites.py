"""Extension Favorites — quick-access favorites list for developers.

Lightweight favorites with ordering, pinning, and usage frequency tracking.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Favorite:
    extension_id: str
    pinned: bool = False
    access_count: int = 0
    added_at: float = 0.0
    last_accessed: float = 0.0

    def __post_init__(self):
        if not self.added_at:
            self.added_at = time.time()


class ExtensionFavoritesService:
    """Manages developer extension favorites."""

    MAX_FAVORITES = 50

    def __init__(self):
        self._favs: dict[str, dict[str, Favorite]] = defaultdict(dict)

    def add(self, user_id: str, extension_id: str) -> Favorite | dict:
        if extension_id in self._favs[user_id]:
            return self._favs[user_id][extension_id]
        if len(self._favs[user_id]) >= self.MAX_FAVORITES:
            return {"error": "Max favorites reached"}
        fav = Favorite(extension_id=extension_id)
        self._favs[user_id][extension_id] = fav
        return fav

    def remove(self, user_id: str, extension_id: str) -> bool:
        return self._favs[user_id].pop(extension_id, None) is not None

    def toggle_pin(self, user_id: str, extension_id: str) -> bool:
        fav = self._favs.get(user_id, {}).get(extension_id)
        if fav:
            fav.pinned = not fav.pinned
            return True
        return False

    def access(self, user_id: str, extension_id: str) -> None:
        fav = self._favs.get(user_id, {}).get(extension_id)
        if fav:
            fav.access_count += 1
            fav.last_accessed = time.time()

    def get_favorites(self, user_id: str) -> list[Favorite]:
        favs = list(self._favs.get(user_id, {}).values())
        # Pinned first, then by access count
        return sorted(favs, key=lambda f: (-int(f.pinned), -f.access_count))

    def is_favorite(self, user_id: str, extension_id: str) -> bool:
        return extension_id in self._favs.get(user_id, {})

    def get_count(self, user_id: str) -> int:
        return len(self._favs.get(user_id, {}))

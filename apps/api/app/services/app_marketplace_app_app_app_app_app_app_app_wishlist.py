"""App wishlist — save and manage app wishlists for later installation."""
from __future__ import annotations


class Wishlist:
    def __init__(self):
        self._lists: dict[str, list[str]] = {}

    def add(self, user_id: str, app_id: str) -> dict:
        self._lists.setdefault(user_id, [])
        if app_id in self._lists[user_id]:
            return {"added": False, "reason": "already_in_wishlist"}
        self._lists[user_id].append(app_id)
        return {"added": True, "count": len(self._lists[user_id])}

    def remove(self, user_id: str, app_id: str) -> dict:
        lst = self._lists.get(user_id, [])
        if app_id not in lst:
            return {"removed": False}
        lst.remove(app_id)
        return {"removed": True, "count": len(lst)}

    def get_list(self, user_id: str) -> list[str]:
        return list(self._lists.get(user_id, []))

    def is_wishlisted(self, user_id: str, app_id: str) -> bool:
        return app_id in self._lists.get(user_id, [])

    def count(self, user_id: str) -> int:
        return len(self._lists.get(user_id, []))

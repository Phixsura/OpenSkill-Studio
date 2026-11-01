"""Changelog subscribe — manage per-app changelog subscriptions."""
from __future__ import annotations


class ChangelogSubscriptionManager:
    def __init__(self):
        self._subs: dict[str, set[str]] = {}  # app_id -> set of user_ids

    def subscribe(self, app_id: str, user_id: str) -> dict:
        self._subs.setdefault(app_id, set()).add(user_id)
        return {"subscribed": True, "app_id": app_id, "count": len(self._subs[app_id])}

    def unsubscribe(self, app_id: str, user_id: str) -> dict:
        subs = self._subs.get(app_id, set())
        subs.discard(user_id)
        return {"unsubscribed": True, "count": len(subs)}

    def is_subscribed(self, app_id: str, user_id: str) -> bool:
        return user_id in self._subs.get(app_id, set())

    def get_subscribers(self, app_id: str) -> list[str]:
        return sorted(self._subs.get(app_id, set()))

    def subscriber_count(self, app_id: str) -> int:
        return len(self._subs.get(app_id, set()))

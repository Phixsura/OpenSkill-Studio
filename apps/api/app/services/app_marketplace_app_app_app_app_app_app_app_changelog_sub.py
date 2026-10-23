"""Changelog subscriber — manage user subscriptions to product updates."""
from __future__ import annotations


class ChangelogSubscriber:
    def __init__(self):
        self._subscribers: dict[str, dict] = {}

    def subscribe(self, *, email: str, categories: list[str] | None = None,
                   frequency: str = "weekly") -> dict:
        self._subscribers[email] = {
            "email": email, "categories": categories or ["all"],
            "frequency": frequency, "active": True,
        }
        return {"email": email, "subscribed": True, "frequency": frequency}

    def unsubscribe(self, email: str) -> dict:
        if email in self._subscribers:
            self._subscribers[email]["active"] = False
            return {"unsubscribed": True}
        return {"error": "Not subscribed"}

    def list_active(self, *, category: str | None = None) -> list[dict]:
        subs = [s for s in self._subscribers.values() if s["active"]]
        if category:
            subs = [s for s in subs if "all" in s["categories"] or category in s["categories"]]
        return [{"email": s["email"], "frequency": s["frequency"]} for s in subs]

    def stats(self) -> dict:
        active = sum(1 for s in self._subscribers.values() if s["active"])
        return {"total": len(self._subscribers), "active": active,
                "inactive": len(self._subscribers) - active}

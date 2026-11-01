"""Webhook subscription manager — manage event subscriptions and delivery."""
from __future__ import annotations


class WebhookSubscriptionManager:
    def __init__(self):
        self._subscriptions: dict[str, dict] = {}

    def subscribe(self, sub_id: str, url: str, events: list[str], secret: str = "") -> dict:
        self._subscriptions[sub_id] = {"id": sub_id, "url": url, "events": events,
                                        "secret": secret, "active": True, "deliveries": 0}
        return self._subscriptions[sub_id]

    def unsubscribe(self, sub_id: str) -> dict:
        if sub_id in self._subscriptions:
            self._subscriptions[sub_id]["active"] = False
            return {"id": sub_id, "unsubscribed": True}
        return {"id": sub_id, "unsubscribed": False}

    def dispatch(self, event_type: str) -> dict:
        targets = []
        for sub in self._subscriptions.values():
            if sub["active"] and event_type in sub["events"]:
                sub["deliveries"] += 1
                targets.append({"id": sub["id"], "url": sub["url"]})
        return {"event": event_type, "dispatched_to": len(targets), "targets": targets}

    def list_subscriptions(self, event_type: str = "") -> list[dict]:
        subs = [s for s in self._subscriptions.values() if s["active"]]
        if event_type:
            subs = [s for s in subs if event_type in s["events"]]
        return subs

    def stats(self) -> dict:
        active = sum(1 for s in self._subscriptions.values() if s["active"])
        total_deliveries = sum(s["deliveries"] for s in self._subscriptions.values())
        return {"total": len(self._subscriptions), "active": active, "deliveries": total_deliveries}

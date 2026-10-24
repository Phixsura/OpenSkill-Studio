"""Event bus — publish-subscribe event system."""

from __future__ import annotations
import html
from collections import defaultdict
from datetime import datetime, timezone


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[dict]] = defaultdict(list)
        self._history: list[dict] = []

    def subscribe(self, *, event: str, handler_id: str, name: str = "") -> dict:
        sub = {"handler_id": handler_id, "name": html.escape(name), "event": event,
               "subscribed_at": datetime.now(timezone.utc).isoformat()}
        self._subscribers[event].append(sub)
        return sub

    def publish(self, *, event: str, payload: dict | None = None) -> dict:
        subs = self._subscribers.get(event, [])
        entry = {"event": event, "payload": payload or {}, "subscriber_count": len(subs),
                 "timestamp": datetime.now(timezone.utc).isoformat()}
        self._history.append(entry)
        return entry

    def list_subscriptions(self) -> dict:
        all_subs = []
        for event, subs in self._subscribers.items():
            for s in subs:
                all_subs.append(s)
        return {"subscriptions": all_subs, "total": len(all_subs),
                "event_types": list(self._subscribers.keys())}

    def history(self, *, limit: int = 20) -> dict:
        items = self._history[-limit:]
        items.reverse()
        return {"events": items, "total": len(self._history)}

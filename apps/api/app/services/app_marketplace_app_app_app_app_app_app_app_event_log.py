"""Webhook event log — immutable event log with filtering and search."""
from __future__ import annotations
import secrets
import html


class EventLog:
    def __init__(self):
        self._events: list[dict] = []

    def append(self, *, event_type: str, source: str, payload: dict,
                actor: str = "") -> dict:
        eid = f"evt_{secrets.token_hex(6)}"
        self._events.append({
            "id": eid, "type": event_type, "source": html.escape(source),
            "payload": payload, "actor": actor,
        })
        return {"id": eid, "type": event_type}

    def query(self, *, event_type: str | None = None, source: str | None = None,
               limit: int = 50) -> list[dict]:
        result = self._events
        if event_type:
            result = [e for e in result if e["type"] == event_type]
        if source:
            result = [e for e in result if e["source"] == source]
        return [{"id": e["id"], "type": e["type"], "source": e["source"],
                 "actor": e["actor"]} for e in reversed(result[-limit:])]

    def count_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._events:
            counts[e["type"]] = counts.get(e["type"], 0) + 1
        return counts

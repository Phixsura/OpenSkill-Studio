"""Event replay engine — replay events from a specific point in time."""
from __future__ import annotations


class EventReplayEngine:
    def __init__(self):
        self._events: list[dict] = []

    def store(self, event_type: str, payload: dict, timestamp: float) -> dict:
        event = {"type": event_type, "payload": payload, "timestamp": timestamp,
                 "seq": len(self._events) + 1}
        self._events.append(event)
        return event

    def replay(self, from_seq: int = 1, to_seq: int | None = None,
               event_type: str = "") -> dict:
        filtered = self._events
        if event_type:
            filtered = [e for e in filtered if e["type"] == event_type]
        filtered = [e for e in filtered if e["seq"] >= from_seq]
        if to_seq:
            filtered = [e for e in filtered if e["seq"] <= to_seq]
        return {"events": filtered, "count": len(filtered),
                "from_seq": from_seq, "to_seq": to_seq or "latest"}

    def stats(self) -> dict:
        types = set(e["type"] for e in self._events)
        return {"total_events": len(self._events), "event_types": len(types)}

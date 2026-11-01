"""Event sourcing store — append-only event log with projections."""
from __future__ import annotations


class EventStore:
    def __init__(self):
        self._streams: dict[str, list[dict]] = {}

    def append(self, stream_id: str, event_type: str, data: dict) -> dict:
        self._streams.setdefault(stream_id, [])
        version = len(self._streams[stream_id]) + 1
        event = {"stream_id": stream_id, "version": version,
                 "type": event_type, "data": data}
        self._streams[stream_id].append(event)
        return event

    def read(self, stream_id: str, from_version: int = 1) -> list[dict]:
        events = self._streams.get(stream_id, [])
        return [e for e in events if e["version"] >= from_version]

    def project(self, stream_id: str, reducer: callable, initial: dict | None = None) -> dict:
        state = dict(initial or {})
        for event in self.read(stream_id):
            state = reducer(state, event)
        return state

    def stats(self) -> dict:
        total = sum(len(v) for v in self._streams.values())
        return {"streams": len(self._streams), "total_events": total}

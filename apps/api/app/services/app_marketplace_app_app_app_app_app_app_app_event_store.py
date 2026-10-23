"""Event sourcing store — append-only event log with projection support."""
from __future__ import annotations


class EventStore:
    def __init__(self):
        self._streams: dict[str, list[dict]] = {}
        self._global_seq = 0

    def append(self, stream_id: str, *, event_type: str, data: dict) -> dict:
        self._global_seq += 1
        event = {"seq": self._global_seq, "stream": stream_id,
                 "type": event_type, "data": data}
        self._streams.setdefault(stream_id, []).append(event)
        return {"seq": self._global_seq, "stream": stream_id, "type": event_type}

    def read_stream(self, stream_id: str, *, after_seq: int = 0) -> list[dict]:
        return [e for e in self._streams.get(stream_id, []) if e["seq"] > after_seq]

    def project(self, stream_id: str, reducer: callable, initial: dict | None = None) -> dict:
        state = dict(initial or {})
        events = self._streams.get(stream_id, [])
        for e in events:
            state = reducer(state, e)
        return {"state": state, "version": len(events)}

    def stats(self) -> dict:
        total_events = sum(len(s) for s in self._streams.values())
        return {"streams": len(self._streams), "total_events": total_events,
                "global_seq": self._global_seq}

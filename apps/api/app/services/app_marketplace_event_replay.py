"""Event Replay — replay historical events for debugging and recovery.

Stores an event log and allows replaying events to specific extensions
or time ranges for debugging webhook issues or recovering state.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class StoredEvent:
    event_id: str
    event_type: str
    extension_id: str
    payload: dict
    timestamp: str
    replayed: bool = False
    replay_count: int = 0


class EventReplayService:
    """Stores and replays extension events for debugging."""

    def __init__(self, max_events: int = 100000):
        self._events: list[StoredEvent] = []
        self._max = max_events

    def store(self, event_id: str, event_type: str, extension_id: str,
              payload: dict) -> StoredEvent:
        """Store an event for potential replay."""
        event = StoredEvent(
            event_id=event_id, event_type=event_type,
            extension_id=extension_id, payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._events.append(event)
        if len(self._events) > self._max:
            self._events = self._events[-self._max:]
        return event

    def query(self, extension_id: str | None = None, event_type: str | None = None,
              from_time: str = "", to_time: str = "", limit: int = 100) -> list[StoredEvent]:
        """Query stored events with filters."""
        results = list(self._events)
        if extension_id:
            results = [e for e in results if e.extension_id == extension_id]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if from_time:
            results = [e for e in results if e.timestamp >= from_time]
        if to_time:
            results = [e for e in results if e.timestamp <= to_time]
        return results[-limit:]

    def replay(self, event_ids: list[str]) -> list[dict]:
        """Replay specific events. Returns replay results."""
        results = []
        events_by_id = {e.event_id: e for e in self._events}
        for eid in event_ids:
            event = events_by_id.get(eid)
            if event:
                event.replayed = True
                event.replay_count += 1
                results.append({
                    "event_id": eid, "status": "replayed",
                    "event_type": event.event_type,
                    "replay_count": event.replay_count,
                })
            else:
                results.append({"event_id": eid, "status": "not_found"})
        return results

    def replay_range(self, extension_id: str, from_time: str, to_time: str) -> list[dict]:
        """Replay all events in a time range for an extension."""
        events = self.query(extension_id=extension_id, from_time=from_time,
                           to_time=to_time, limit=10000)
        return self.replay([e.event_id for e in events])

    def get_replay_stats(self, extension_id: str) -> dict:
        events = [e for e in self._events if e.extension_id == extension_id]
        return {
            "extension_id": extension_id,
            "total_stored": len(events),
            "total_replayed": sum(1 for e in events if e.replayed),
            "event_types": list(set(e.event_type for e in events)),
        }

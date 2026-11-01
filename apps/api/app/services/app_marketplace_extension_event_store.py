"""Event Sourcing Store — append-only event log with aggregate projection.

Implements:
- Append-only event log per aggregate
- Version-based optimistic concurrency
- Snapshot support for fast replay
- Event type filtering and time range queries
- Aggregate state rebuild from events
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from copy import deepcopy


@dataclass
class DomainEvent:
    event_id: str
    aggregate_id: str
    event_type: str
    data: dict
    version: int
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


@dataclass
class Snapshot:
    aggregate_id: str
    state: dict
    version: int
    timestamp: float = 0.0


class EventStoreService:
    def __init__(self):
        self._events: dict[str, list[DomainEvent]] = {}  # agg_id -> events
        self._snapshots: dict[str, Snapshot] = {}
        self._counter = 0

    def append(self, aggregate_id: str, event_type: str, data: dict,
               expected_version: int = -1) -> DomainEvent:
        """Append event with optimistic concurrency check."""
        events = self._events.get(aggregate_id, [])
        current_version = events[-1].version if events else 0

        if expected_version >= 0 and current_version != expected_version:
            raise ValueError(
                f"Concurrency conflict: expected v{expected_version}, "
                f"current v{current_version}")

        self._counter += 1
        new_version = current_version + 1
        event = DomainEvent(
            event_id=f"evt-{self._counter}", aggregate_id=aggregate_id,
            event_type=event_type, data=data, version=new_version)

        if aggregate_id not in self._events:
            self._events[aggregate_id] = []
        self._events[aggregate_id].append(event)
        return event

    def get_events(self, aggregate_id: str, after_version: int = 0,
                   event_type: str | None = None) -> list[DomainEvent]:
        events = self._events.get(aggregate_id, [])
        result = [e for e in events if e.version > after_version]
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        return result

    def save_snapshot(self, aggregate_id: str, state: dict) -> Snapshot:
        events = self._events.get(aggregate_id, [])
        version = events[-1].version if events else 0
        snap = Snapshot(aggregate_id=aggregate_id, state=deepcopy(state),
                        version=version, timestamp=time.time())
        self._snapshots[aggregate_id] = snap
        return snap

    def get_snapshot(self, aggregate_id: str) -> Snapshot | None:
        return self._snapshots.get(aggregate_id)

    def rebuild(self, aggregate_id: str,
                reducer: callable) -> dict:
        """Rebuild aggregate state by replaying events from last snapshot."""
        snap = self._snapshots.get(aggregate_id)
        state = deepcopy(snap.state) if snap else {}
        after = snap.version if snap else 0
        events = self.get_events(aggregate_id, after_version=after)
        for event in events:
            state = reducer(state, event)
        return state

    def get_version(self, aggregate_id: str) -> int:
        events = self._events.get(aggregate_id, [])
        return events[-1].version if events else 0

    def get_all_aggregate_ids(self) -> list[str]:
        return list(self._events.keys())

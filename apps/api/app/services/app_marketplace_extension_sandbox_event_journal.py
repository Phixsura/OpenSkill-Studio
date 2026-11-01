"""Sandbox Event Journal — append-only event log for sandbox audit trail.

Records immutable events with sequence numbers, event types, metadata,
and provides replay, range queries, and compaction.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class JournalEvent:
    sequence: int
    event_type: str
    data: dict
    actor: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class SandboxEventJournalService:
    """Append-only event journal for sandbox audit trails."""

    MAX_EVENTS = 10000

    def __init__(self):
        self._journals: dict[str, list[JournalEvent]] = defaultdict(list)
        self._sequences: dict[str, int] = defaultdict(int)

    def append(self, sandbox_id: str, event_type: str, data: dict,
               actor: str = "") -> JournalEvent:
        self._sequences[sandbox_id] += 1
        event = JournalEvent(
            sequence=self._sequences[sandbox_id],
            event_type=event_type, data=data, actor=actor,
        )
        journal = self._journals[sandbox_id]
        journal.append(event)
        if len(journal) > self.MAX_EVENTS:
            self._journals[sandbox_id] = journal[-self.MAX_EVENTS:]
        return event

    def get_range(self, sandbox_id: str, from_seq: int = 0,
                  to_seq: int = 0, limit: int = 100) -> list[JournalEvent]:
        journal = self._journals.get(sandbox_id, [])
        if from_seq:
            journal = [e for e in journal if e.sequence >= from_seq]
        if to_seq:
            journal = [e for e in journal if e.sequence <= to_seq]
        return journal[:limit]

    def get_by_type(self, sandbox_id: str, event_type: str,
                    limit: int = 100) -> list[JournalEvent]:
        return [e for e in self._journals.get(sandbox_id, [])
                if e.event_type == event_type][-limit:]

    def get_by_actor(self, sandbox_id: str, actor: str) -> list[JournalEvent]:
        return [e for e in self._journals.get(sandbox_id, [])
                if e.actor == actor]

    def get_latest(self, sandbox_id: str, count: int = 10) -> list[JournalEvent]:
        return self._journals.get(sandbox_id, [])[-count:]

    def get_sequence(self, sandbox_id: str) -> int:
        return self._sequences.get(sandbox_id, 0)

    def replay(self, sandbox_id: str, from_seq: int = 1) -> list[JournalEvent]:
        return [e for e in self._journals.get(sandbox_id, [])
                if e.sequence >= from_seq]

    def get_stats(self, sandbox_id: str) -> dict:
        journal = self._journals.get(sandbox_id, [])
        types: dict[str, int] = defaultdict(int)
        for e in journal:
            types[e.event_type] += 1
        return {
            "total_events": len(journal),
            "current_sequence": self._sequences.get(sandbox_id, 0),
            "event_types": dict(types),
        }

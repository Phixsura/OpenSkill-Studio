"""Change Data Capture — stream data mutations as ordered events.

Implements:
- Capture INSERT, UPDATE, DELETE operations
- Before/after snapshots for updates
- Ordered change log with monotonic sequence numbers
- Consumer offsets for at-least-once delivery
- Filtering by table, operation type, column
- Debounce rapid changes to same key
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import defaultdict


@dataclass
class ChangeEvent:
    sequence: int
    table: str
    operation: str  # INSERT, UPDATE, DELETE
    key: str
    before: dict | None = None
    after: dict | None = None
    timestamp: float = 0.0
    changed_columns: list[str] = field(default_factory=list)


class CdcService:
    def __init__(self):
        self._log: list[ChangeEvent] = []
        self._sequence = 0
        self._consumers: dict[str, int] = {}  # consumer -> last acked sequence
        self._debounce: dict[str, float] = {}  # key -> last change time
        self._debounce_ms: float = 0  # 0 = disabled

    def set_debounce(self, ms: float) -> None:
        self._debounce_ms = ms

    def capture_insert(self, table: str, key: str, data: dict) -> ChangeEvent:
        return self._capture(table, "INSERT", key, before=None, after=data)

    def capture_update(self, table: str, key: str, before: dict,
                       after: dict) -> ChangeEvent | None:
        # Compute changed columns
        changed = [k for k in set(before) | set(after)
                   if before.get(k) != after.get(k)]
        if not changed:
            return None  # no actual changes

        return self._capture(table, "UPDATE", key, before=before, after=after,
                             changed_columns=changed)

    def capture_delete(self, table: str, key: str, data: dict) -> ChangeEvent:
        return self._capture(table, "DELETE", key, before=data, after=None)

    def _capture(self, table: str, operation: str, key: str,
                 before: dict | None, after: dict | None,
                 changed_columns: list[str] | None = None) -> ChangeEvent | None:
        now = time.time()
        # Debounce check
        if self._debounce_ms > 0:
            debounce_key = f"{table}:{key}"
            last = self._debounce.get(debounce_key, 0)
            if (now - last) * 1000 < self._debounce_ms:
                # Update last event in place instead of creating new
                for evt in reversed(self._log):
                    if evt.table == table and evt.key == key:
                        evt.after = after
                        evt.changed_columns = changed_columns or []
                        evt.timestamp = now
                        return evt
            self._debounce[debounce_key] = now

        self._sequence += 1
        event = ChangeEvent(sequence=self._sequence, table=table,
                            operation=operation, key=key,
                            before=before, after=after,
                            timestamp=now,
                            changed_columns=changed_columns or [])
        self._log.append(event)
        return event

    def subscribe(self, consumer_id: str, start_from: int = 0) -> None:
        self._consumers[consumer_id] = start_from

    def poll(self, consumer_id: str, max_events: int = 100,
             table: str | None = None,
             operations: list[str] | None = None) -> list[ChangeEvent]:
        """Poll for new events after consumer's last offset."""
        offset = self._consumers.get(consumer_id, 0)
        events = [e for e in self._log if e.sequence > offset]

        if table:
            events = [e for e in events if e.table == table]
        if operations:
            events = [e for e in events if e.operation in operations]

        return events[:max_events]

    def ack(self, consumer_id: str, sequence: int) -> None:
        """Acknowledge processing up to a sequence number."""
        self._consumers[consumer_id] = max(
            self._consumers.get(consumer_id, 0), sequence)

    def get_changes_for_key(self, table: str, key: str) -> list[ChangeEvent]:
        """Full change history for a specific key."""
        return [e for e in self._log if e.table == table and e.key == key]

    def get_current_state(self, table: str) -> dict[str, dict]:
        """Reconstruct current state from change log."""
        state: dict[str, dict] = {}
        for event in self._log:
            if event.table != table:
                continue
            if event.operation in ("INSERT", "UPDATE") and event.after:
                state[event.key] = event.after
            elif event.operation == "DELETE":
                state.pop(event.key, None)
        return state

    def stats(self) -> dict:
        by_table: dict[str, int] = defaultdict(int)
        by_op: dict[str, int] = defaultdict(int)
        for e in self._log:
            by_table[e.table] += 1
            by_op[e.operation] += 1
        return {
            "total_events": len(self._log),
            "sequence": self._sequence,
            "consumers": len(self._consumers),
            "by_table": dict(by_table),
            "by_operation": dict(by_op),
        }

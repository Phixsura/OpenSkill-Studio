"""API Consumer Event Replay Buffer — buffer events for replay during outages."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class BufferedEvent:
    event_id: str
    event_type: str
    consumer_id: str
    payload_hash: str
    buffered_at: float = field(default_factory=time.time)
    replayed: bool = False
    size_bytes: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEventReplayBuffer:
    def __init__(self, max_buffer_size: int = 10000, retention_hours: int = 24) -> None:
        self._buffer: dict[str, list[BufferedEvent]] = {}
        self._max = max(100, max_buffer_size)
        self._retention_s = max(1, retention_hours) * 3600

    def buffer_event(self, installation_id: str, event: BufferedEvent) -> BufferedEvent:
        if not installation_id: raise ValueError("installation_id is required")
        buf = self._buffer.setdefault(installation_id, [])
        buf.append(event)
        if len(buf) > self._max: self._buffer[installation_id] = buf[-self._max:]
        return event

    def replay_all(self, installation_id: str, consumer_id: str) -> list[BufferedEvent]:
        events = [e for e in self._buffer.get(installation_id, []) if e.consumer_id == consumer_id and not e.replayed]
        for e in events: e.replayed = True
        return events

    def pending_count(self, installation_id: str, consumer_id: str | None = None) -> int:
        events = [e for e in self._buffer.get(installation_id, []) if not e.replayed]
        if consumer_id: events = [e for e in events if e.consumer_id == consumer_id]
        return len(events)

    def total_buffered(self, installation_id: str) -> int:
        return len(self._buffer.get(installation_id, []))

    def buffer_size_bytes(self, installation_id: str) -> int:
        return sum(e.size_bytes for e in self._buffer.get(installation_id, []))

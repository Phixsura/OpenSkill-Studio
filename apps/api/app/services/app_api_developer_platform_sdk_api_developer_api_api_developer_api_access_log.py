"""App API Developer API Access Log — structured API access logging with filtering."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AccessLogEntry:
    entry_id: str
    consumer_id: str
    method: str
    path: str
    status_code: int
    latency_ms: float
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLog:
    def __init__(self, max_entries: int = 50000) -> None:
        self._max = max(1, max_entries)
        self._log: dict[str, list[AccessLogEntry]] = {}

    def record(self, installation_id: str, entry_id: str, consumer_id: str, method: str, path: str, status_code: int, latency_ms: float) -> AccessLogEntry:
        if not installation_id: raise ValueError("installation_id is required")
        e = AccessLogEntry(entry_id=entry_id, consumer_id=consumer_id, method=method.upper(), path=path, status_code=status_code, latency_ms=latency_ms)
        entries = self._log.setdefault(installation_id, [])
        entries.append(e)
        if len(entries) > self._max: self._log[installation_id] = entries[-self._max:]
        return e

    def search(self, installation_id: str, consumer_id: str | None = None, method: str | None = None, min_status: int | None = None, min_latency: float | None = None, limit: int = 50) -> list[AccessLogEntry]:
        entries = self._log.get(installation_id, [])
        if consumer_id: entries = [e for e in entries if e.consumer_id == consumer_id]
        if method: entries = [e for e in entries if e.method == method.upper()]
        if min_status: entries = [e for e in entries if e.status_code >= min_status]
        if min_latency: entries = [e for e in entries if e.latency_ms >= min_latency]
        return list(reversed(entries[-limit:]))

    def error_count(self, installation_id: str) -> int:
        return sum(1 for e in self._log.get(installation_id, []) if e.status_code >= 400)

    def total(self, installation_id: str) -> int:
        return len(self._log.get(installation_id, []))

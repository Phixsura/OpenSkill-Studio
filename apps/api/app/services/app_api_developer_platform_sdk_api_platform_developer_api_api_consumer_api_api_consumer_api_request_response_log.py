"""API Consumer Request Response Log — structured request/response pair logging."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

_REDACT_HEADERS = {"authorization", "cookie", "x-api-key", "x-auth-token"}

@dataclass
class RequestResponsePair:
    pair_id: str
    method: str
    path: str
    request_status: int
    duration_ms: float
    consumer_id: str = ""
    request_size: int = 0
    response_size: int = 0
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLog:
    def __init__(self, max_entries: int = 10000) -> None:
        self._log: dict[str, list[RequestResponsePair]] = {}
        self._max = max(500, max_entries)

    def record(self, installation_id: str, pair: RequestResponsePair) -> RequestResponsePair:
        if not installation_id: raise ValueError("installation_id is required")
        entries = self._log.setdefault(installation_id, [])
        entries.append(pair)
        if len(entries) > self._max: self._log[installation_id] = entries[-self._max:]
        return pair

    def query(self, installation_id: str, consumer_id: str | None = None, method: str | None = None, status_min: int | None = None, limit: int = 50) -> list[RequestResponsePair]:
        entries = self._log.get(installation_id, [])
        if consumer_id: entries = [e for e in entries if e.consumer_id == consumer_id]
        if method: entries = [e for e in entries if e.method == method.upper()]
        if status_min is not None: entries = [e for e in entries if e.request_status >= status_min]
        return list(reversed(entries[-limit:]))

    def total_bandwidth(self, installation_id: str) -> int:
        return sum(e.request_size + e.response_size for e in self._log.get(installation_id, []))

    def avg_duration(self, installation_id: str) -> float:
        entries = self._log.get(installation_id, [])
        if not entries: return 0.0
        return round(sum(e.duration_ms for e in entries) / len(entries), 2)

    def entry_count(self, installation_id: str) -> int:
        return len(self._log.get(installation_id, []))

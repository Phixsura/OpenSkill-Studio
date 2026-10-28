"""App API Request Log — structured request logging.

Manages API request logs:
- Log requests with method, path, status, duration
- Filter by status range or path
- Aggregate stats per path
- Per-installation scoped logs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class RequestLogEntry:
    """A logged API request."""

    log_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    timestamp: float = field(default_factory=time.time)


class AppAPIRequestLog:
    """Structured request logging."""

    def __init__(self, max_entries: int = 5000) -> None:
        self._max = max(1, max_entries)
        self._logs: dict[str, list[RequestLogEntry]] = {}

    def log_request(
        self, installation_id: str, log_id: str, method: str, path: str,
        status_code: int, duration_ms: float,
    ) -> RequestLogEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        entry = RequestLogEntry(
            log_id=log_id, method=method.upper(), path=path,
            status_code=status_code, duration_ms=duration_ms,
        )
        entries = self._logs.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._logs[installation_id] = entries[-self._max:]
        return entry

    def recent(self, installation_id: str, limit: int = 50) -> list[RequestLogEntry]:
        return list(reversed(self._logs.get(installation_id, [])[-limit:]))

    def errors(self, installation_id: str) -> list[RequestLogEntry]:
        return [e for e in self._logs.get(installation_id, []) if e.status_code >= 400]

    def path_stats(self, installation_id: str) -> list[dict]:
        paths: dict[str, list[float]] = {}
        for e in self._logs.get(installation_id, []):
            paths.setdefault(e.path, []).append(e.duration_ms)
        return sorted([
            {"path": p, "count": len(ds), "avg_ms": round(sum(ds) / len(ds), 1)}
            for p, ds in paths.items()
        ], key=lambda x: x["count"], reverse=True)

    def count(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))

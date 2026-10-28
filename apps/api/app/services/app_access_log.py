"""App Access Log — structured HTTP request logging for installed apps.

Records API request/response pairs with timing:
- Request method, path, status code
- Response time tracking
- Per-installation scoped logs
- Aggregation: requests per endpoint, error rates
- Configurable retention limit
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class AccessEntry:
    """A single access log entry."""

    entry_id: str
    installation_id: str
    method: str
    path: str
    status_code: int
    response_time_ms: float
    user_agent: str = ""
    ip_address: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class EndpointStats:
    """Aggregated stats for an endpoint."""

    method: str
    path: str
    total_requests: int
    error_count: int
    avg_response_ms: float
    p95_response_ms: float
    error_rate_pct: float


class AppAccessLog:
    """Structured HTTP request logging for installed apps."""

    def __init__(self, max_entries: int = 10000) -> None:
        self._entries: list[AccessEntry] = []
        self._max = max(100, max_entries)

    def record(
        self,
        installation_id: str,
        entry_id: str,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float,
        user_agent: str = "",
        ip_address: str = "",
        now: float | None = None,
    ) -> AccessEntry:
        """Record an access log entry."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not method:
            raise ValueError("method is required")
        if not path:
            raise ValueError("path is required")
        if status_code < 100 or status_code > 599:
            raise ValueError("status_code must be 100-599")

        entry = AccessEntry(
            entry_id=entry_id,
            installation_id=installation_id,
            method=method.upper(),
            path=path,
            status_code=status_code,
            response_time_ms=max(0.0, response_time_ms),
            user_agent=user_agent,
            ip_address=ip_address,
            timestamp=now or time.time(),
        )
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry

    def query(
        self,
        installation_id: str,
        method: str | None = None,
        path: str | None = None,
        status_min: int | None = None,
        status_max: int | None = None,
        limit: int = 50,
    ) -> list[AccessEntry]:
        """Query entries with filters, newest first."""
        if not installation_id:
            raise ValueError("installation_id is required")
        results = [e for e in self._entries if e.installation_id == installation_id]
        if method:
            results = [e for e in results if e.method == method.upper()]
        if path:
            results = [e for e in results if e.path == path]
        if status_min is not None:
            results = [e for e in results if e.status_code >= status_min]
        if status_max is not None:
            results = [e for e in results if e.status_code <= status_max]
        return list(reversed(results[-limit:]))

    def get_endpoint_stats(
        self, installation_id: str
    ) -> list[EndpointStats]:
        """Get aggregated stats per endpoint."""
        buckets: dict[tuple[str, str], list[AccessEntry]] = {}
        for e in self._entries:
            if e.installation_id != installation_id:
                continue
            key = (e.method, e.path)
            buckets.setdefault(key, []).append(e)

        stats = []
        for (method, path), entries in sorted(buckets.items()):
            times = sorted(e.response_time_ms for e in entries)
            errors = sum(1 for e in entries if e.status_code >= 400)
            total = len(entries)
            p95_idx = int(0.95 * len(times)) - 1
            stats.append(EndpointStats(
                method=method,
                path=path,
                total_requests=total,
                error_count=errors,
                avg_response_ms=round(sum(times) / total, 2),
                p95_response_ms=times[max(0, p95_idx)],
                error_rate_pct=round(errors / total * 100, 2) if total > 0 else 0.0,
            ))
        return stats

    def error_rate(self, installation_id: str) -> float:
        """Overall error rate percentage."""
        entries = [e for e in self._entries if e.installation_id == installation_id]
        if not entries:
            return 0.0
        errors = sum(1 for e in entries if e.status_code >= 400)
        return round(errors / len(entries) * 100, 2)

    def count(self, installation_id: str) -> int:
        return sum(1 for e in self._entries if e.installation_id == installation_id)

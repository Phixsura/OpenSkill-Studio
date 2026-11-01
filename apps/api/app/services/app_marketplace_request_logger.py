"""Request Logger — structured HTTP request logging for extension APIs.

Captures request/response pairs with timing, headers, and body
for debugging, analytics, and compliance auditing.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RequestLog:
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    extension_id: str
    org_id: str = ""
    request_size: int = 0
    response_size: int = 0
    error: str = ""
    timestamp: str = ""
    ip_address: str = ""
    user_agent: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class RequestLogger:
    """Structured request logging with analytics."""

    def __init__(self, max_logs: int = 50000):
        self._logs: list[RequestLog] = []
        self._max_logs = max_logs
        self._counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def log(self, entry: RequestLog) -> None:
        """Record a request log entry."""
        self._logs.append(entry)
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]

        # Update counters
        key = entry.extension_id
        self._counters[key]["total"] += 1
        self._counters[key][f"status_{entry.status_code // 100}xx"] += 1
        if entry.status_code >= 400:
            self._counters[key]["errors"] += 1

    def query(self, extension_id: str | None = None, method: str | None = None,
              min_status: int = 0, max_status: int = 999,
              min_duration_ms: float = 0, limit: int = 100) -> list[RequestLog]:
        """Query logs with filters."""
        results = list(self._logs)
        if extension_id:
            results = [r for r in results if r.extension_id == extension_id]
        if method:
            results = [r for r in results if r.method == method]
        results = [r for r in results if min_status <= r.status_code <= max_status]
        if min_duration_ms > 0:
            results = [r for r in results if r.duration_ms >= min_duration_ms]
        return results[-limit:]

    def get_slow_requests(self, extension_id: str, threshold_ms: float = 1000,
                          limit: int = 20) -> list[RequestLog]:
        return self.query(extension_id=extension_id, min_duration_ms=threshold_ms, limit=limit)

    def get_error_requests(self, extension_id: str, limit: int = 20) -> list[RequestLog]:
        return self.query(extension_id=extension_id, min_status=400, limit=limit)

    def get_summary(self, extension_id: str) -> dict:
        counters = self._counters.get(extension_id, {})
        total = counters.get("total", 0)
        errors = counters.get("errors", 0)
        logs = [l for l in self._logs if l.extension_id == extension_id]
        avg_duration = round(sum(l.duration_ms for l in logs) / max(1, len(logs)), 2)
        return {
            "extension_id": extension_id,
            "total_requests": total,
            "error_count": errors,
            "error_rate": round(errors / max(1, total) * 100, 2),
            "avg_duration_ms": avg_duration,
            "status_2xx": counters.get("status_2xx", 0),
            "status_4xx": counters.get("status_4xx", 0),
            "status_5xx": counters.get("status_5xx", 0),
        }

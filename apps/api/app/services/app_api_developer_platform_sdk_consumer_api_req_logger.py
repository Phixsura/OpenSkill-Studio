"""Consumer API Request Logger — structured request logging with search."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class LogEntry:
    log_id: str
    consumer_id: str
    endpoint_id: str
    method: str
    status_code: int
    latency_ms: float
    timestamp: str = ""
    ip_address: str = ""
    user_agent: str = ""
    level: str = "info"  # debug, info, warn, error


@dataclass
class RequestLogger:
    """Structured API request logging with search and filtering."""

    _logs: list[LogEntry] = field(default_factory=list)
    _max_logs: int = 50000

    def log(self, entry: LogEntry) -> dict:
        if entry.level not in ("debug", "info", "warn", "error"):
            raise ValueError(f"Invalid log level: {entry.level}")
        if len(self._logs) >= self._max_logs:
            self._logs = self._logs[-(self._max_logs // 2):]
        # Auto-set level from status code
        if entry.status_code >= 500:
            entry.level = "error"
        elif entry.status_code >= 400:
            entry.level = "warn"
        self._logs.append(entry)
        return {"log_id": entry.log_id, "level": entry.level, "total": len(self._logs)}

    def search(self, consumer_id: str | None = None, endpoint_id: str | None = None,
               level: str | None = None, method: str | None = None,
               status_min: int | None = None, status_max: int | None = None,
               limit: int = 50) -> list[dict]:
        results = list(reversed(self._logs))
        if consumer_id:
            results = [r for r in results if r.consumer_id == consumer_id]
        if endpoint_id:
            results = [r for r in results if r.endpoint_id == endpoint_id]
        if level:
            results = [r for r in results if r.level == level]
        if method:
            results = [r for r in results if r.method == method.upper()]
        if status_min is not None:
            results = [r for r in results if r.status_code >= status_min]
        if status_max is not None:
            results = [r for r in results if r.status_code <= status_max]
        return [
            {"log_id": r.log_id, "consumer_id": r.consumer_id,
             "endpoint_id": r.endpoint_id, "method": r.method,
             "status_code": r.status_code, "latency_ms": r.latency_ms,
             "level": r.level, "timestamp": r.timestamp}
            for r in results[:limit]
        ]

    def get_summary(self, consumer_id: str | None = None) -> dict:
        logs = self._logs
        if consumer_id:
            logs = [l for l in logs if l.consumer_id == consumer_id]
        if not logs:
            return {"total": 0}
        by_level = {}
        for lvl in ("debug", "info", "warn", "error"):
            by_level[lvl] = sum(1 for l in logs if l.level == lvl)
        avg_latency = sum(l.latency_ms for l in logs) / len(logs)
        return {
            "total": len(logs),
            "by_level": by_level,
            "avg_latency_ms": round(avg_latency, 2),
            "error_rate": round(by_level.get("error", 0) / len(logs) * 100, 2),
        }

    def tail(self, count: int = 10) -> list[dict]:
        return self.search(limit=count)

    def count(self) -> int:
        return len(self._logs)

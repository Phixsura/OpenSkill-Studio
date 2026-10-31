"""API Request Logger — structured request/response logging with redaction."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

_REDACT_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token", "proxy-authorization"}

@dataclass
class RequestLog:
    log_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    request_size_bytes: int = 0
    response_size_bytes: int = 0
    consumer_id: str = ""
    ip_address: str = ""
    timestamp: float = field(default_factory=time.time)
    error: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLogger:
    def __init__(self, max_logs: int = 50000) -> None:
        self._logs: dict[str, list[RequestLog]] = {}
        self._max = max(1000, max_logs)

    def log_request(self, installation_id: str, entry: RequestLog) -> RequestLog:
        if not installation_id: raise ValueError("installation_id is required")
        entries = self._logs.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._logs[installation_id] = entries[-self._max:]
        return entry

    def query(self, installation_id: str, method: str | None = None, status_min: int | None = None, status_max: int | None = None, consumer_id: str | None = None, limit: int = 100) -> list[RequestLog]:
        entries = self._logs.get(installation_id, [])
        if method: entries = [e for e in entries if e.method == method.upper()]
        if status_min is not None: entries = [e for e in entries if e.status_code >= status_min]
        if status_max is not None: entries = [e for e in entries if e.status_code <= status_max]
        if consumer_id: entries = [e for e in entries if e.consumer_id == consumer_id]
        return list(reversed(entries[-limit:]))

    def error_logs(self, installation_id: str, limit: int = 50) -> list[RequestLog]:
        return self.query(installation_id, status_min=500, limit=limit)

    def stats(self, installation_id: str) -> dict[str, object]:
        entries = self._logs.get(installation_id, [])
        if not entries: return {"total": 0, "errors": 0, "avg_duration_ms": 0, "total_bytes_in": 0, "total_bytes_out": 0}
        errors = sum(1 for e in entries if e.status_code >= 500)
        avg_dur = round(sum(e.duration_ms for e in entries) / len(entries), 2)
        bytes_in = sum(e.request_size_bytes for e in entries)
        bytes_out = sum(e.response_size_bytes for e in entries)
        return {"total": len(entries), "errors": errors, "avg_duration_ms": avg_dur, "total_bytes_in": bytes_in, "total_bytes_out": bytes_out}

    def count(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))

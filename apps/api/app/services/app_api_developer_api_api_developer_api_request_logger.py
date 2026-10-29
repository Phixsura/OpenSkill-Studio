"""App API Developer API Request Logger — structured request/response logging."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

_SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key", "x-auth-token"}

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
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiDeveloperApiRequestLogger:
    def __init__(self, max_logs: int = 10000) -> None:
        self._max = max(1, max_logs)
        self._logs: dict[str, list[RequestLog]] = {}

    def log_request(self, installation_id: str, log_id: str, method: str, path: str, status_code: int, duration_ms: float, request_size_bytes: int = 0, response_size_bytes: int = 0, consumer_id: str = "", headers: dict | None = None) -> RequestLog:
        if not installation_id: raise ValueError("installation_id is required")
        # Scrub sensitive headers before any processing
        if headers:
            headers = {k: ("[REDACTED]" if k.lower() in _SENSITIVE_HEADERS else v) for k, v in headers.items()}
        entry = RequestLog(log_id=log_id, method=method.upper(), path=path, status_code=status_code, duration_ms=duration_ms, request_size_bytes=request_size_bytes, response_size_bytes=response_size_bytes, consumer_id=consumer_id)
        logs = self._logs.setdefault(installation_id, [])
        logs.append(entry)
        if len(logs) > self._max: self._logs[installation_id] = logs[-self._max:]
        return entry

    def search(self, installation_id: str, method: str | None = None, path: str | None = None, min_status: int | None = None, consumer_id: str | None = None, limit: int = 50) -> list[RequestLog]:
        logs = self._logs.get(installation_id, [])
        if method: logs = [l for l in logs if l.method == method.upper()]
        if path: logs = [l for l in logs if l.path == path]
        if min_status: logs = [l for l in logs if l.status_code >= min_status]
        if consumer_id: logs = [l for l in logs if l.consumer_id == consumer_id]
        return list(reversed(logs[-limit:]))

    def error_logs(self, installation_id: str) -> list[RequestLog]:
        return [l for l in self._logs.get(installation_id, []) if l.status_code >= 400]

    def total(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))

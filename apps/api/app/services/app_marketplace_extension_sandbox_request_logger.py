"""Sandbox Request Logger — structured request/response logging."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
import time, secrets

@dataclass
class RequestLogEntry:
    log_id: str
    method: str
    path: str
    status_code: int
    latency_ms: float
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()

class SandboxRequestLoggerService:
    def __init__(self):
        self._logs: dict[str, list[RequestLogEntry]] = defaultdict(list)

    def log(self, sandbox_id: str, method: str, path: str,
            status_code: int, latency_ms: float) -> RequestLogEntry:
        entry = RequestLogEntry(f"rl_{secrets.token_urlsafe(6)}", method, path, status_code, latency_ms)
        self._logs[sandbox_id].append(entry)
        if len(self._logs[sandbox_id]) > 1000:
            self._logs[sandbox_id] = self._logs[sandbox_id][-1000:]
        return entry

    def query(self, sandbox_id: str, method: str | None = None,
              min_status: int = 0, limit: int = 50) -> list[RequestLogEntry]:
        entries = self._logs.get(sandbox_id, [])
        if method: entries = [e for e in entries if e.method == method]
        if min_status: entries = [e for e in entries if e.status_code >= min_status]
        return entries[-limit:]

    def get_stats(self, sandbox_id: str) -> dict:
        entries = self._logs.get(sandbox_id, [])
        if not entries: return {"total": 0, "avg_latency": 0, "error_count": 0}
        return {
            "total": len(entries),
            "avg_latency": round(sum(e.latency_ms for e in entries) / len(entries), 1),
            "error_count": sum(1 for e in entries if e.status_code >= 400),
        }

"""App API Developer API Playground Runner — execute API calls in sandbox."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class PlaygroundExecution:
    execution_id: str
    method: str
    path: str
    status_code: int
    response_body: str
    duration_ms: float
    executed_at: float = field(default_factory=time.time)
    headers_sent: dict[str, str] = field(default_factory=dict)

class AppAPIDeveloperAPIApiPlaygroundRunner:
    def __init__(self, max_history: int = 100) -> None:
        self._max = max(1, max_history)
        self._history: dict[str, list[PlaygroundExecution]] = {}

    def execute(self, installation_id: str, execution_id: str, method: str, path: str, status_code: int, response_body: str, duration_ms: float, headers_sent: dict[str, str] | None = None) -> PlaygroundExecution:
        if not installation_id: raise ValueError("installation_id is required")
        if method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError("invalid HTTP method")
        e = PlaygroundExecution(execution_id=execution_id, method=method.upper(), path=path, status_code=status_code, response_body=response_body[:10000], duration_ms=duration_ms, headers_sent=headers_sent or {})
        hist = self._history.setdefault(installation_id, [])
        hist.append(e)
        if len(hist) > self._max: self._history[installation_id] = hist[-self._max:]
        return e

    def history(self, installation_id: str, limit: int = 20) -> list[PlaygroundExecution]:
        return list(reversed(self._history.get(installation_id, [])[-limit:]))

    def by_status(self, installation_id: str, min_status: int) -> list[PlaygroundExecution]:
        return [e for e in self._history.get(installation_id, []) if e.status_code >= min_status]

    def avg_duration(self, installation_id: str) -> float:
        hist = self._history.get(installation_id, [])
        if not hist: return 0.0
        return round(sum(e.duration_ms for e in hist) / len(hist), 2)

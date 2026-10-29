"""App API Developer API Playground — interactive API explorer with history."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class PlaygroundRequest:
    request_id: str
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    status_code: int = 0
    response_preview: str = ""
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    saved: bool = False

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiPlayground:
    def __init__(self, max_history: int = 200) -> None:
        self._max = max(1, max_history)
        self._history: dict[str, list[PlaygroundRequest]] = {}
        self._saved: dict[str, list[PlaygroundRequest]] = {}

    def execute(self, installation_id: str, request_id: str, method: str, path: str, status_code: int, response_preview: str = "", duration_ms: float = 0.0, body: str = "") -> PlaygroundRequest:
        if not installation_id: raise ValueError("installation_id is required")
        if method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError("invalid method")
        r = PlaygroundRequest(request_id=request_id, method=method.upper(), path=path, body=body[:5000], status_code=status_code, response_preview=response_preview[:2000], duration_ms=duration_ms)
        hist = self._history.setdefault(installation_id, [])
        hist.append(r)
        if len(hist) > self._max: self._history[installation_id] = hist[-self._max:]
        return r

    def save(self, installation_id: str, request_id: str) -> PlaygroundRequest:
        hist = self._history.get(installation_id, [])
        r = next((r for r in hist if r.request_id == request_id), None)
        if r is None: raise KeyError(f"Request {request_id} not found")
        r.saved = True
        self._saved.setdefault(installation_id, []).append(r)
        return r

    def history(self, installation_id: str, limit: int = 20) -> list[PlaygroundRequest]:
        return list(reversed(self._history.get(installation_id, [])[-limit:]))

    def saved_requests(self, installation_id: str) -> list[PlaygroundRequest]:
        return self._saved.get(installation_id, [])

    def stats(self, installation_id: str) -> dict[str, int]:
        hist = self._history.get(installation_id, [])
        return {"total": len(hist), "saved": len(self._saved.get(installation_id, [])), "errors": sum(1 for r in hist if r.status_code >= 400)}

"""API Consumer Request Inspector — inspect and debug API requests in real-time."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

_REDACT_HEADERS = {"authorization", "cookie", "x-api-key", "x-auth-token", "proxy-authorization"}

@dataclass
class InspectedRequest:
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    request_headers: dict[str, str] = field(default_factory=dict)
    response_headers: dict[str, str] = field(default_factory=dict)
    body_preview: str = ""
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestInspector:
    def __init__(self, max_inspections: int = 500) -> None:
        self._inspections: dict[str, list[InspectedRequest]] = {}
        self._max = max(50, max_inspections)

    def inspect(self, installation_id: str, req: InspectedRequest) -> InspectedRequest:
        if not installation_id: raise ValueError("installation_id is required")
        # Redact sensitive headers
        req.request_headers = {k: ("[REDACTED]" if k.lower() in _REDACT_HEADERS else v) for k, v in req.request_headers.items()}
        req.response_headers = {k: ("[REDACTED]" if k.lower() in _REDACT_HEADERS else v) for k, v in req.response_headers.items()}
        if len(req.body_preview) > 2048: req.body_preview = req.body_preview[:2048] + "...[TRUNCATED]"
        entries = self._inspections.setdefault(installation_id, [])
        entries.append(req)
        if len(entries) > self._max: self._inspections[installation_id] = entries[-self._max:]
        return req

    def recent(self, installation_id: str, limit: int = 20, method: str | None = None, status_min: int | None = None) -> list[InspectedRequest]:
        entries = self._inspections.get(installation_id, [])
        if method: entries = [e for e in entries if e.method == method.upper()]
        if status_min is not None: entries = [e for e in entries if e.status_code >= status_min]
        return list(reversed(entries[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._inspections.get(installation_id, []))

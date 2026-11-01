"""API Consumer Request Abort Controller — cancel in-flight requests."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AbortableRequest:
    request_id: str
    consumer_id: str
    endpoint: str
    started_at: float = field(default_factory=time.time)
    aborted: bool = False
    abort_reason: str = ""
    completed: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortController:
    def __init__(self) -> None:
        self._requests: dict[tuple[str, str], AbortableRequest] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def register(self, installation_id: str, request: AbortableRequest) -> AbortableRequest:
        if not installation_id: raise ValueError("installation_id is required")
        self._requests[(installation_id, request.request_id)] = request
        return request

    def abort(self, installation_id: str, request_id: str, reason: str = "user_cancelled") -> AbortableRequest:
        key = (installation_id, request_id)
        req = self._requests.get(key)
        if req is None: raise KeyError(f"Request {request_id} not found")
        if req.completed: raise ValueError("Cannot abort completed request")
        req.aborted = True
        req.abort_reason = reason
        stats = self._stats.setdefault(installation_id, {"aborted": 0, "completed": 0})
        stats["aborted"] += 1
        return req

    def complete(self, installation_id: str, request_id: str) -> AbortableRequest:
        key = (installation_id, request_id)
        req = self._requests.get(key)
        if req is None: raise KeyError(f"Request {request_id} not found")
        if req.aborted: raise ValueError("Cannot complete aborted request")
        req.completed = True
        self._stats.setdefault(installation_id, {"aborted": 0, "completed": 0})["completed"] += 1
        return req

    def is_aborted(self, installation_id: str, request_id: str) -> bool:
        req = self._requests.get((installation_id, request_id))
        return req.aborted if req else False

    def in_flight(self, installation_id: str) -> list[AbortableRequest]:
        return [r for (inst, _), r in self._requests.items() if inst == installation_id and not r.completed and not r.aborted]

    def abort_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"aborted": 0, "completed": 0})
        total = s["aborted"] + s["completed"]
        return round((s["aborted"] / total) * 100, 1) if total > 0 else 0.0

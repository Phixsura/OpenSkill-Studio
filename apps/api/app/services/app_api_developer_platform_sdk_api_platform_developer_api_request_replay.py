"""API Request Replay — capture and replay API requests for debugging."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class ReplayStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class CapturedRequest:
    request_id: str
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    original_status: int = 200
    captured_at: float = field(default_factory=time.time)

@dataclass
class ReplayResult:
    request_id: str
    status: ReplayStatus = ReplayStatus.PENDING
    replayed_at: float = 0.0
    response_status: int = 0
    duration_ms: float = 0.0

_REDACT_HEADERS = {"authorization", "cookie", "x-api-key", "x-auth-token"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplay:
    def __init__(self, max_captures: int = 1000) -> None:
        self._captures: dict[tuple[str, str], CapturedRequest] = {}
        self._replays: dict[tuple[str, str], list[ReplayResult]] = {}
        self._max = max(1, max_captures)
        self._counts: dict[str, int] = {}

    def capture(self, installation_id: str, req: CapturedRequest) -> CapturedRequest:
        if not installation_id: raise ValueError("installation_id is required")
        count = self._counts.get(installation_id, 0)
        if count >= self._max:
            oldest_key = next((k for k in self._captures if k[0] == installation_id), None)
            if oldest_key: del self._captures[oldest_key]; count -= 1
        req.headers = {k: ("[REDACTED]" if k.lower() in _REDACT_HEADERS else v) for k, v in req.headers.items()}
        self._captures[(installation_id, req.request_id)] = req
        self._counts[installation_id] = count + 1
        return req

    def replay(self, installation_id: str, request_id: str, response_status: int, duration_ms: float) -> ReplayResult:
        key = (installation_id, request_id)
        if key not in self._captures: raise KeyError(f"Request {request_id} not found")
        status = ReplayStatus.SUCCESS if 200 <= response_status < 400 else ReplayStatus.FAILED
        result = ReplayResult(request_id=request_id, status=status, replayed_at=time.time(), response_status=response_status, duration_ms=duration_ms)
        self._replays.setdefault(key, []).append(result)
        return result

    def get_captures(self, installation_id: str, method: str | None = None, limit: int = 50) -> list[CapturedRequest]:
        caps = [c for (inst, _), c in self._captures.items() if inst == installation_id]
        if method: caps = [c for c in caps if c.method == method.upper()]
        return caps[-limit:]

    def replay_history(self, installation_id: str, request_id: str) -> list[ReplayResult]:
        return self._replays.get((installation_id, request_id), [])

    def stats(self, installation_id: str) -> dict[str, int]:
        caps = sum(1 for (inst, _) in self._captures if inst == installation_id)
        replays = sum(len(r) for (inst, _), r in self._replays.items() if inst == installation_id)
        successes = sum(1 for (inst, _), rs in self._replays.items() if inst == installation_id for r in rs if r.status == ReplayStatus.SUCCESS)
        return {"captured": caps, "replayed": replays, "successful": successes}

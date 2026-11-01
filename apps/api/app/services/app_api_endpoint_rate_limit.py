"""App API Endpoint Rate Limit — per-endpoint rate limiting."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointRateLimit:
    method: str
    path: str
    max_rpm: int  # requests per minute
    current_count: int = 0
    window_start: float = field(default_factory=time.time)

class AppAPIEndpointRateLimit:
    def __init__(self) -> None:
        self._limits: dict[tuple[str, str, str], EndpointRateLimit] = {}

    def set_limit(self, installation_id: str, method: str, path: str, max_rpm: int) -> EndpointRateLimit:
        if not installation_id: raise ValueError("installation_id is required")
        if max_rpm < 1: raise ValueError("max_rpm must be at least 1")
        rl = EndpointRateLimit(method=method.upper(), path=path, max_rpm=max_rpm)
        self._limits[(installation_id, method.upper(), path)] = rl
        return rl

    def check(self, installation_id: str, method: str, path: str) -> dict:
        key = (installation_id, method.upper(), path)
        rl = self._limits.get(key)
        if rl is None: return {"allowed": True, "limited": False}
        now = time.time()
        if now - rl.window_start >= 60:
            rl.current_count = 1
            rl.window_start = now
            return {"allowed": True, "remaining": rl.max_rpm - 1}
        if rl.current_count >= rl.max_rpm:
            return {"allowed": False, "remaining": 0}
        rl.current_count += 1
        return {"allowed": True, "remaining": rl.max_rpm - rl.current_count}

    def list_limits(self, installation_id: str) -> list[EndpointRateLimit]:
        return [rl for (inst, _, _), rl in self._limits.items() if inst == installation_id]

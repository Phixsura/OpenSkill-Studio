"""API Rate Limit Window — sliding window rate limiting with burst support."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WindowConfig:
    window_seconds: int = 60
    max_requests: int = 100
    burst_limit: int = 20  # max in any 1-second sub-window

@dataclass
class WindowState:
    consumer_id: str
    config: WindowConfig
    timestamps: list[float] = field(default_factory=list)

    def _prune(self, now: float) -> None:
        cutoff = now - self.config.window_seconds
        self.timestamps = [t for t in self.timestamps if t > cutoff]

    @property
    def count(self) -> int:
        self._prune(time.time())
        return len(self.timestamps)

    @property
    def remaining(self) -> int:
        return max(0, self.config.max_requests - self.count)

    def check_burst(self, now: float) -> bool:
        one_sec_ago = now - 1.0
        burst_count = sum(1 for t in self.timestamps if t > one_sec_ago)
        return burst_count < self.config.burst_limit

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindow:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str, str], WindowState] = {}

    def configure(self, installation_id: str, consumer_id: str, endpoint: str, config: WindowConfig) -> WindowState:
        if not installation_id: raise ValueError("installation_id is required")
        if config.window_seconds < 1: raise ValueError("window must be >= 1s")
        if config.max_requests < 1: raise ValueError("max_requests must be >= 1")
        key = (installation_id, consumer_id, endpoint)
        state = WindowState(consumer_id=consumer_id, config=config)
        self._windows[key] = state
        return state

    def check(self, installation_id: str, consumer_id: str, endpoint: str) -> dict[str, object]:
        key = (installation_id, consumer_id, endpoint)
        state = self._windows.get(key)
        if state is None: return {"allowed": True, "reason": "no_config"}
        now = time.time()
        state._prune(now)
        if len(state.timestamps) >= state.config.max_requests:
            return {"allowed": False, "reason": "window_limit", "remaining": 0, "retry_after_s": round(state.config.window_seconds - (now - state.timestamps[0]), 1)}
        if not state.check_burst(now):
            return {"allowed": False, "reason": "burst_limit", "remaining": state.remaining, "retry_after_s": 1.0}
        return {"allowed": True, "remaining": state.remaining}

    def record(self, installation_id: str, consumer_id: str, endpoint: str) -> None:
        key = (installation_id, consumer_id, endpoint)
        state = self._windows.get(key)
        if state: state.timestamps.append(time.time())

    def get_state(self, installation_id: str, consumer_id: str, endpoint: str) -> WindowState | None:
        return self._windows.get((installation_id, consumer_id, endpoint))

    def list_consumers(self, installation_id: str) -> list[str]:
        seen: set[str] = set()
        return [cid for (inst, cid, _) in self._windows if inst == installation_id and not (cid in seen or seen.add(cid))]

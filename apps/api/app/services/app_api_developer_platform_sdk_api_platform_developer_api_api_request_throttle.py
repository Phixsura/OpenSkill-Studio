"""API Request Throttle — per-consumer concurrent request throttling."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ThrottleConfig:
    consumer_id: str
    max_concurrent: int = 10
    queue_timeout_s: int = 30

@dataclass
class ThrottleState:
    consumer_id: str
    active_requests: int = 0
    queued_requests: int = 0
    total_throttled: int = 0
    total_served: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestThrottle:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], ThrottleConfig] = {}
        self._states: dict[tuple[str, str], ThrottleState] = {}

    def configure(self, installation_id: str, consumer_id: str, max_concurrent: int = 10, queue_timeout_s: int = 30) -> ThrottleConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if max_concurrent < 1: raise ValueError("max_concurrent must be >= 1")
        if queue_timeout_s < 0: raise ValueError("queue_timeout must be non-negative")
        config = ThrottleConfig(consumer_id=consumer_id, max_concurrent=max_concurrent, queue_timeout_s=queue_timeout_s)
        self._configs[(installation_id, consumer_id)] = config
        self._states.setdefault((installation_id, consumer_id), ThrottleState(consumer_id=consumer_id))
        return config

    def acquire(self, installation_id: str, consumer_id: str) -> dict[str, object]:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return {"allowed": True, "reason": "no_config"}
        state = self._states[(installation_id, consumer_id)]
        if state.active_requests >= config.max_concurrent:
            state.total_throttled += 1
            return {"allowed": False, "reason": "max_concurrent", "active": state.active_requests, "limit": config.max_concurrent}
        state.active_requests += 1
        state.total_served += 1
        return {"allowed": True, "active": state.active_requests}

    def release(self, installation_id: str, consumer_id: str) -> ThrottleState:
        state = self._states.get((installation_id, consumer_id))
        if state is None: raise KeyError(f"No state for {consumer_id}")
        state.active_requests = max(0, state.active_requests - 1)
        return state

    def get_state(self, installation_id: str, consumer_id: str) -> ThrottleState:
        return self._states.get((installation_id, consumer_id), ThrottleState(consumer_id=consumer_id))

    def throttle_rate(self, installation_id: str, consumer_id: str) -> float:
        state = self._states.get((installation_id, consumer_id))
        if state is None or (state.total_served + state.total_throttled) == 0: return 0.0
        total = state.total_served + state.total_throttled
        return round((state.total_throttled / total) * 100, 1)

    def list_configs(self, installation_id: str) -> list[ThrottleConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

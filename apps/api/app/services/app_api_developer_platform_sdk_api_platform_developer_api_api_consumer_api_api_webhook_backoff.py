"""API Consumer Webhook Backoff — manage exponential backoff for failed deliveries."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class BackoffState:
    consumer_id: str
    endpoint: str
    attempt: int = 0
    base_delay_s: int = 1
    max_delay_s: int = 3600
    multiplier: float = 2.0
    current_delay_s: int = 0

    def next_delay(self) -> int:
        delay = int(self.base_delay_s * (self.multiplier ** self.attempt))
        return min(delay, self.max_delay_s)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoff:
    def __init__(self) -> None:
        self._states: dict[tuple[str, str, str], BackoffState] = {}

    def configure(self, installation_id: str, consumer_id: str, endpoint: str, base_delay_s: int = 1, max_delay_s: int = 3600, multiplier: float = 2.0) -> BackoffState:
        if not installation_id: raise ValueError("installation_id is required")
        if base_delay_s < 1: raise ValueError("base_delay must be >= 1")
        if multiplier < 1.1: raise ValueError("multiplier must be >= 1.1")
        state = BackoffState(consumer_id=consumer_id, endpoint=endpoint, base_delay_s=base_delay_s, max_delay_s=max_delay_s, multiplier=multiplier)
        self._states[(installation_id, consumer_id, endpoint)] = state
        return state

    def record_failure(self, installation_id: str, consumer_id: str, endpoint: str) -> BackoffState:
        key = (installation_id, consumer_id, endpoint)
        state = self._states.get(key)
        if state is None: raise KeyError(f"No backoff for {consumer_id}/{endpoint}")
        state.attempt += 1
        state.current_delay_s = state.next_delay()
        return state

    def record_success(self, installation_id: str, consumer_id: str, endpoint: str) -> BackoffState:
        key = (installation_id, consumer_id, endpoint)
        state = self._states.get(key)
        if state is None: raise KeyError(f"No backoff for {consumer_id}/{endpoint}")
        state.attempt = 0
        state.current_delay_s = 0
        return state

    def get_delay(self, installation_id: str, consumer_id: str, endpoint: str) -> int:
        state = self._states.get((installation_id, consumer_id, endpoint))
        return state.current_delay_s if state else 0

    def backed_off_endpoints(self, installation_id: str) -> list[BackoffState]:
        return [s for (inst, _, _), s in self._states.items() if inst == installation_id and s.attempt > 0]

    def list_states(self, installation_id: str) -> list[BackoffState]:
        return [s for (inst, _, _), s in self._states.items() if inst == installation_id]

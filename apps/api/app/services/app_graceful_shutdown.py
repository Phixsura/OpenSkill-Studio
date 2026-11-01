"""App Graceful Shutdown — manage graceful shutdown for app processes.

Tracks shutdown state for installed apps:
- Register shutdown hooks
- Track in-flight requests during shutdown
- Drain timeout management
- Per-installation scoped shutdown state
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ShutdownPhase(str, Enum):
    RUNNING = "running"
    DRAINING = "draining"
    SHUTDOWN = "shutdown"


@dataclass
class ShutdownState:
    """Current shutdown state for an installation."""

    installation_id: str
    phase: ShutdownPhase = ShutdownPhase.RUNNING
    in_flight_requests: int = 0
    drain_timeout_seconds: int = 30
    initiated_at: float | None = None
    completed_at: float | None = None
    hooks_registered: int = 0
    hooks_completed: int = 0


class AppGracefulShutdown:
    """Manage graceful shutdown for app processes."""

    def __init__(self) -> None:
        self._states: dict[str, ShutdownState] = {}

    def register(
        self,
        installation_id: str,
        drain_timeout_seconds: int = 30,
        hooks_count: int = 0,
    ) -> ShutdownState:
        if not installation_id:
            raise ValueError("installation_id is required")
        if drain_timeout_seconds < 1:
            raise ValueError("drain_timeout must be >= 1")

        state = ShutdownState(
            installation_id=installation_id,
            drain_timeout_seconds=drain_timeout_seconds,
            hooks_registered=hooks_count,
        )
        self._states[installation_id] = state
        return state

    def initiate_shutdown(
        self, installation_id: str, in_flight: int = 0, now: float | None = None
    ) -> ShutdownState:
        state = self._get(installation_id)
        if state.phase != ShutdownPhase.RUNNING:
            raise ValueError(f"Cannot initiate shutdown in {state.phase} phase")
        state.phase = ShutdownPhase.DRAINING
        state.in_flight_requests = max(0, in_flight)
        state.initiated_at = now or time.time()
        return state

    def update_in_flight(self, installation_id: str, count: int) -> ShutdownState:
        state = self._get(installation_id)
        state.in_flight_requests = max(0, count)
        return state

    def complete_hook(self, installation_id: str) -> ShutdownState:
        state = self._get(installation_id)
        state.hooks_completed = min(state.hooks_completed + 1, state.hooks_registered)
        return state

    def complete_shutdown(self, installation_id: str, now: float | None = None) -> ShutdownState:
        state = self._get(installation_id)
        if state.phase != ShutdownPhase.DRAINING:
            raise ValueError("Not in draining phase")
        state.phase = ShutdownPhase.SHUTDOWN
        state.completed_at = now or time.time()
        state.in_flight_requests = 0
        return state

    def is_ready_to_shutdown(self, installation_id: str, now: float | None = None) -> bool:
        """Check if all requests drained and hooks completed."""
        state = self._get(installation_id)
        if state.phase != ShutdownPhase.DRAINING:
            return False
        if state.in_flight_requests > 0:
            # Check drain timeout
            now = now or time.time()
            if state.initiated_at and (now - state.initiated_at) < state.drain_timeout_seconds:
                return False
        return state.hooks_completed >= state.hooks_registered

    def get_state(self, installation_id: str) -> ShutdownState:
        return self._get(installation_id)

    def _get(self, installation_id: str) -> ShutdownState:
        state = self._states.get(installation_id)
        if state is None:
            raise KeyError(f"Installation {installation_id} not registered")
        return state

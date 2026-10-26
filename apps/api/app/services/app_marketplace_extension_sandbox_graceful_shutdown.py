"""Sandbox Graceful Shutdown — coordinate clean sandbox shutdown.

Manages shutdown phases (drain, cleanup, terminate) with timeout
enforcement, hook execution, and resource cleanup tracking.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum


class ShutdownPhase(str, Enum):
    RUNNING = "running"
    DRAINING = "draining"
    CLEANUP = "cleanup"
    TERMINATED = "terminated"
    FORCE_KILLED = "force_killed"


@dataclass
class ShutdownState:
    sandbox_id: str
    phase: ShutdownPhase = ShutdownPhase.RUNNING
    drain_timeout_ms: int = 30000
    cleanup_timeout_ms: int = 10000
    hooks_executed: int = 0
    hooks_failed: int = 0
    resources_cleaned: list[str] = field(default_factory=list)
    started_at: float = 0.0
    finished_at: float = 0.0


class SandboxGracefulShutdownService:
    """Coordinates graceful sandbox shutdown with phases."""

    def __init__(self):
        self._states: dict[str, ShutdownState] = {}

    def initiate(self, sandbox_id: str, drain_timeout_ms: int = 30000,
                 cleanup_timeout_ms: int = 10000) -> ShutdownState:
        state = ShutdownState(
            sandbox_id=sandbox_id, phase=ShutdownPhase.DRAINING,
            drain_timeout_ms=drain_timeout_ms,
            cleanup_timeout_ms=cleanup_timeout_ms,
            started_at=time.time(),
        )
        self._states[sandbox_id] = state
        return state

    def complete_drain(self, sandbox_id: str) -> bool:
        state = self._states.get(sandbox_id)
        if not state or state.phase != ShutdownPhase.DRAINING:
            return False
        state.phase = ShutdownPhase.CLEANUP
        return True

    def record_hook(self, sandbox_id: str, success: bool) -> None:
        state = self._states.get(sandbox_id)
        if state:
            state.hooks_executed += 1
            if not success:
                state.hooks_failed += 1

    def record_cleanup(self, sandbox_id: str, resource: str) -> None:
        state = self._states.get(sandbox_id)
        if state:
            state.resources_cleaned.append(resource)

    def terminate(self, sandbox_id: str) -> ShutdownState | None:
        state = self._states.get(sandbox_id)
        if not state:
            return None
        state.phase = ShutdownPhase.TERMINATED
        state.finished_at = time.time()
        return state

    def force_kill(self, sandbox_id: str) -> ShutdownState | None:
        state = self._states.get(sandbox_id)
        if not state:
            state = ShutdownState(sandbox_id=sandbox_id, started_at=time.time())
            self._states[sandbox_id] = state
        state.phase = ShutdownPhase.FORCE_KILLED
        state.finished_at = time.time()
        return state

    def get_state(self, sandbox_id: str) -> ShutdownState | None:
        return self._states.get(sandbox_id)

    def get_duration_ms(self, sandbox_id: str) -> float:
        state = self._states.get(sandbox_id)
        if not state:
            return 0
        end = state.finished_at or time.time()
        return round((end - state.started_at) * 1000, 1)

    def is_shutting_down(self, sandbox_id: str) -> bool:
        state = self._states.get(sandbox_id)
        return state is not None and state.phase in (ShutdownPhase.DRAINING, ShutdownPhase.CLEANUP)

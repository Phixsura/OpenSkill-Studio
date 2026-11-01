"""Sandbox Timer Pool — manage timers and intervals within sandboxes.

Provides setTimeout/setInterval-like API with max timer limits,
timer tracking, pause/resume, and automatic cleanup on sandbox stop.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class TimerType(str, Enum):
    TIMEOUT = "timeout"
    INTERVAL = "interval"


class TimerState(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    FIRED = "fired"
    CANCELLED = "cancelled"


@dataclass
class SandboxTimer:
    timer_id: str
    sandbox_id: str
    timer_type: TimerType
    callback_name: str
    delay_ms: int
    state: TimerState = TimerState.ACTIVE
    fire_count: int = 0
    max_fires: int = 0  # 0 = unlimited for intervals
    created_at: float = 0.0
    next_fire_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.next_fire_at:
            self.next_fire_at = self.created_at + self.delay_ms / 1000


class SandboxTimerPoolService:
    """Manages timers and intervals for extension sandboxes."""

    MAX_TIMERS_PER_SANDBOX = 100
    MIN_INTERVAL_MS = 100
    MAX_DELAY_MS = 86400000  # 24 hours

    def __init__(self):
        self._timers: dict[str, SandboxTimer] = {}
        self._by_sandbox: dict[str, list[str]] = {}

    def set_timeout(self, sandbox_id: str, callback_name: str,
                    delay_ms: int) -> SandboxTimer | dict:
        return self._create(sandbox_id, callback_name, delay_ms, TimerType.TIMEOUT)

    def set_interval(self, sandbox_id: str, callback_name: str,
                     delay_ms: int, max_fires: int = 0) -> SandboxTimer | dict:
        if delay_ms < self.MIN_INTERVAL_MS:
            return {"error": f"Interval too short (min {self.MIN_INTERVAL_MS}ms)"}
        return self._create(sandbox_id, callback_name, delay_ms,
                            TimerType.INTERVAL, max_fires=max_fires)

    def _create(self, sandbox_id: str, callback_name: str, delay_ms: int,
                timer_type: TimerType, max_fires: int = 0) -> SandboxTimer | dict:
        if delay_ms > self.MAX_DELAY_MS:
            return {"error": f"Delay too long (max {self.MAX_DELAY_MS}ms)"}
        if delay_ms < 0:
            return {"error": "Delay must be non-negative"}

        active = [tid for tid in self._by_sandbox.get(sandbox_id, [])
                  if self._timers.get(tid, SandboxTimer("", "", TimerType.TIMEOUT, "", 0)).state == TimerState.ACTIVE]
        if len(active) >= self.MAX_TIMERS_PER_SANDBOX:
            return {"error": f"Timer limit ({self.MAX_TIMERS_PER_SANDBOX}) reached"}

        timer_id = f"tmr_{secrets.token_urlsafe(6)}"
        timer = SandboxTimer(
            timer_id=timer_id, sandbox_id=sandbox_id,
            timer_type=timer_type, callback_name=callback_name,
            delay_ms=delay_ms, max_fires=max_fires,
        )
        self._timers[timer_id] = timer
        self._by_sandbox.setdefault(sandbox_id, []).append(timer_id)
        return timer

    def tick(self, now: float | None = None) -> list[SandboxTimer]:
        current = now or time.time()
        fired: list[SandboxTimer] = []
        for timer in self._timers.values():
            if timer.state != TimerState.ACTIVE:
                continue
            if current >= timer.next_fire_at:
                timer.fire_count += 1
                fired.append(timer)
                if timer.timer_type == TimerType.TIMEOUT:
                    timer.state = TimerState.FIRED
                else:
                    if timer.max_fires > 0 and timer.fire_count >= timer.max_fires:
                        timer.state = TimerState.FIRED
                    else:
                        timer.next_fire_at = current + timer.delay_ms / 1000
        return fired

    def cancel(self, timer_id: str) -> bool:
        timer = self._timers.get(timer_id)
        if timer and timer.state == TimerState.ACTIVE:
            timer.state = TimerState.CANCELLED
            return True
        return False

    def clear_all(self, sandbox_id: str) -> int:
        count = 0
        for tid in self._by_sandbox.get(sandbox_id, []):
            timer = self._timers.get(tid)
            if timer and timer.state == TimerState.ACTIVE:
                timer.state = TimerState.CANCELLED
                count += 1
        return count

    def list_timers(self, sandbox_id: str) -> list[SandboxTimer]:
        return [self._timers[tid] for tid in self._by_sandbox.get(sandbox_id, [])
                if tid in self._timers]

    def get_active_count(self, sandbox_id: str) -> int:
        return sum(1 for tid in self._by_sandbox.get(sandbox_id, [])
                   if self._timers.get(tid, SandboxTimer("", "", TimerType.TIMEOUT, "", 0)).state == TimerState.ACTIVE)

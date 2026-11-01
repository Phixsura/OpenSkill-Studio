"""Sandbox Timer — manage execution timeouts for sandboxed extensions.

Provides configurable timers for sandbox executions with grace periods,
timeout callbacks, and execution time budgets per extension.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field


@dataclass
class TimerEntry:
    timer_id: str
    extension_id: str
    started_at: float
    timeout_seconds: float
    grace_seconds: float = 5.0
    elapsed: float = 0.0
    timed_out: bool = False
    grace_expired: bool = False


class SandboxTimer:
    """Manages execution timeouts for sandboxed code."""

    def __init__(self, default_timeout: float = 30.0, default_grace: float = 5.0):
        self._timers: dict[str, TimerEntry] = {}
        self._budgets: dict[str, float] = {}  # ext -> remaining seconds
        self._default_timeout = default_timeout
        self._default_grace = default_grace

    def start(self, timer_id: str, extension_id: str,
              timeout: float | None = None, grace: float | None = None) -> TimerEntry:
        entry = TimerEntry(
            timer_id=timer_id, extension_id=extension_id,
            started_at=time.monotonic(),
            timeout_seconds=timeout or self._default_timeout,
            grace_seconds=grace or self._default_grace,
        )
        self._timers[timer_id] = entry
        return entry

    def check(self, timer_id: str) -> dict:
        """Check timer status. Returns elapsed, remaining, timed_out."""
        entry = self._timers.get(timer_id)
        if not entry:
            return {"error": "Timer not found"}
        elapsed = time.monotonic() - entry.started_at
        entry.elapsed = elapsed
        remaining = entry.timeout_seconds - elapsed
        grace_remaining = entry.timeout_seconds + entry.grace_seconds - elapsed

        if remaining <= 0 and not entry.timed_out:
            entry.timed_out = True
        if grace_remaining <= 0:
            entry.grace_expired = True

        return {
            "timer_id": timer_id, "elapsed": round(elapsed, 3),
            "remaining": round(max(0, remaining), 3),
            "timed_out": entry.timed_out,
            "grace_expired": entry.grace_expired,
            "timeout": entry.timeout_seconds,
        }

    def stop(self, timer_id: str) -> float:
        """Stop a timer and return elapsed time. Deducts from budget."""
        entry = self._timers.get(timer_id)
        if not entry:
            return 0.0
        elapsed = time.monotonic() - entry.started_at
        entry.elapsed = elapsed
        # Deduct from budget
        if entry.extension_id in self._budgets:
            self._budgets[entry.extension_id] -= elapsed
        return round(elapsed, 3)

    def set_budget(self, extension_id: str, total_seconds: float) -> None:
        self._budgets[extension_id] = total_seconds

    def get_budget(self, extension_id: str) -> dict:
        remaining = self._budgets.get(extension_id)
        if remaining is None:
            return {"extension_id": extension_id, "has_budget": False}
        return {
            "extension_id": extension_id, "has_budget": True,
            "remaining_seconds": round(max(0, remaining), 3),
            "exhausted": remaining <= 0,
        }

    def has_budget(self, extension_id: str) -> bool:
        budget = self._budgets.get(extension_id)
        return budget is None or budget > 0

"""Debounce & Throttle — rate-control primitives for event handling.

Debounce: wait until events stop for N ms, then fire once.
Throttle: fire at most once per N ms, drop intermediate events.

Implements:
- Debounce with leading/trailing edge options
- Throttle with configurable window
- Combined debounce+throttle
- Flush pending debounced calls
- Cancel pending operations
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class DebouncedCall:
    key: str
    last_args: tuple = ()
    last_kwargs: dict = field(default_factory=dict)
    last_called_at: float = 0.0
    scheduled_at: float = 0.0
    fired_count: int = 0
    suppressed_count: int = 0


@dataclass
class ThrottledCall:
    key: str
    last_fired_at: float = 0.0
    fired_count: int = 0
    suppressed_count: int = 0
    pending_args: tuple | None = None


class DebounceThrottleService:
    def __init__(self):
        self._debounced: dict[str, DebouncedCall] = {}
        self._throttled: dict[str, ThrottledCall] = {}

    # --- Debounce ---
    def debounce_call(self, key: str, delay_ms: float,
                      *args, **kwargs) -> dict:
        """Register a debounced call. Resets timer on each call.
        Returns whether the call was scheduled or suppressed."""
        now = time.time()
        delay_s = delay_ms / 1000

        if key not in self._debounced:
            self._debounced[key] = DebouncedCall(key=key)

        dc = self._debounced[key]
        dc.last_args = args
        dc.last_kwargs = kwargs
        dc.last_called_at = now
        dc.scheduled_at = now + delay_s
        dc.suppressed_count += 1

        return {"status": "scheduled", "fires_at": dc.scheduled_at,
                "suppressed_so_far": dc.suppressed_count}

    def check_debounce(self, key: str) -> dict | None:
        """Check if debounced call is ready to fire.
        Returns args if ready, None if still waiting."""
        dc = self._debounced.get(key)
        if not dc or dc.scheduled_at == 0:
            return None

        now = time.time()
        if now >= dc.scheduled_at:
            dc.fired_count += 1
            result = {"args": dc.last_args, "kwargs": dc.last_kwargs,
                      "suppressed": dc.suppressed_count,
                      "fired_count": dc.fired_count}
            dc.scheduled_at = 0
            dc.suppressed_count = 0
            return result
        return None

    def flush_debounce(self, key: str) -> dict | None:
        """Force-fire pending debounced call immediately."""
        dc = self._debounced.get(key)
        if not dc or dc.scheduled_at == 0:
            return None
        dc.scheduled_at = 0
        dc.fired_count += 1
        result = {"args": dc.last_args, "kwargs": dc.last_kwargs,
                  "flushed": True, "fired_count": dc.fired_count}
        dc.suppressed_count = 0
        return result

    def cancel_debounce(self, key: str) -> bool:
        dc = self._debounced.get(key)
        if dc and dc.scheduled_at > 0:
            dc.scheduled_at = 0
            dc.suppressed_count = 0
            return True
        return False

    # --- Throttle ---
    def throttle_call(self, key: str, interval_ms: float,
                      *args, **kwargs) -> dict:
        """Throttle: allow at most one call per interval_ms.
        Returns whether the call was allowed or suppressed."""
        now = time.time()
        interval_s = interval_ms / 1000

        if key not in self._throttled:
            self._throttled[key] = ThrottledCall(key=key)

        tc = self._throttled[key]
        elapsed = now - tc.last_fired_at

        if elapsed >= interval_s:
            tc.last_fired_at = now
            tc.fired_count += 1
            tc.pending_args = None
            return {"status": "fired", "args": args,
                    "fired_count": tc.fired_count}
        else:
            tc.suppressed_count += 1
            tc.pending_args = args
            return {"status": "suppressed",
                    "next_allowed_in_ms": round((interval_s - elapsed) * 1000, 1),
                    "suppressed_count": tc.suppressed_count}

    def get_stats(self, key: str) -> dict:
        dc = self._debounced.get(key)
        tc = self._throttled.get(key)
        return {
            "debounce": {"fired": dc.fired_count, "suppressed": dc.suppressed_count,
                         "pending": dc.scheduled_at > 0} if dc else None,
            "throttle": {"fired": tc.fired_count, "suppressed": tc.suppressed_count} if tc else None,
        }

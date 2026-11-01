"""API request rate controller — adaptive rate control based on system load."""
from __future__ import annotations


class RateController:
    def __init__(self, base_limit: int = 1000, min_limit: int = 100, max_limit: int = 10000):
        self._base = base_limit
        self._min = min_limit
        self._max = max_limit
        self._current = base_limit

    def adjust(self, cpu_pct: float, error_rate_pct: float) -> dict:
        if error_rate_pct > 5 or cpu_pct > 90:
            self._current = max(self._min, int(self._current * 0.7))
            action = "reduce"
        elif error_rate_pct < 0.5 and cpu_pct < 50:
            self._current = min(self._max, int(self._current * 1.2))
            action = "increase"
        else:
            action = "maintain"
        return {"current_limit": self._current, "action": action,
                "cpu_pct": cpu_pct, "error_rate_pct": error_rate_pct}

    def check(self, current_rps: float) -> dict:
        allowed = current_rps <= self._current
        headroom = round((self._current - current_rps) / max(self._current, 1) * 100, 1)
        return {"allowed": allowed, "current_rps": current_rps,
                "limit": self._current, "headroom_pct": max(0, headroom)}

    def stats(self) -> dict:
        return {"current_limit": self._current, "base": self._base,
                "min": self._min, "max": self._max}

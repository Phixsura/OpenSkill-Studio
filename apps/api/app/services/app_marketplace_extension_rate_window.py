"""Rate Window Counter — time-windowed counters for metrics and rate limiting.

Implements:
- Fixed window: count per discrete time bucket
- Sliding window: smooth count using weighted interpolation
- Multi-resolution: track 1s, 1m, 1h windows simultaneously
- Top-K tracking within windows
- Rate calculation (events per second)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import defaultdict


@dataclass
class WindowCounter:
    window_size: float  # seconds
    current_count: int = 0
    previous_count: int = 0
    current_window: int = 0  # window index

    def _window_index(self, now: float) -> int:
        return int(now // self.window_size)

    def increment(self, amount: int = 1, now: float = 0) -> int:
        now = now or time.time()
        idx = self._window_index(now)
        if idx != self.current_window:
            if idx == self.current_window + 1:
                self.previous_count = self.current_count
            else:
                self.previous_count = 0
            self.current_count = 0
            self.current_window = idx
        self.current_count += amount
        return self.current_count

    def get_fixed(self, now: float = 0) -> int:
        """Fixed window: count in current window only."""
        now = now or time.time()
        idx = self._window_index(now)
        if idx != self.current_window:
            return 0
        return self.current_count

    def get_sliding(self, now: float = 0) -> float:
        """Sliding window: weighted interpolation between current and previous."""
        now = now or time.time()
        idx = self._window_index(now)
        if idx != self.current_window:
            if idx == self.current_window + 1:
                elapsed_pct = (now % self.window_size) / self.window_size
                return self.current_count * elapsed_pct
            return 0

        elapsed_pct = (now % self.window_size) / self.window_size
        return self.previous_count * (1 - elapsed_pct) + self.current_count

    def rate_per_second(self, now: float = 0) -> float:
        """Events per second based on sliding window."""
        count = self.get_sliding(now)
        return round(count / self.window_size, 2) if self.window_size > 0 else 0


class RateWindowService:
    def __init__(self):
        self._counters: dict[str, dict[str, WindowCounter]] = defaultdict(dict)
        self._resolutions = [("1s", 1.0), ("1m", 60.0), ("1h", 3600.0)]
        self._top_k: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def configure(self, metric: str, resolutions: list[tuple[str, float]] | None = None) -> None:
        res = resolutions or self._resolutions
        for name, size in res:
            self._counters[metric][name] = WindowCounter(window_size=size)

    def increment(self, metric: str, amount: int = 1,
                  key: str = "") -> None:
        """Increment counter across all resolutions."""
        if metric not in self._counters:
            self.configure(metric)
        now = time.time()
        for counter in self._counters[metric].values():
            counter.increment(amount, now)
        if key:
            self._top_k[metric][key] += amount

    def get(self, metric: str, resolution: str = "1m") -> dict:
        """Get count at a specific resolution."""
        counter = self._counters.get(metric, {}).get(resolution)
        if not counter:
            return {"fixed": 0, "sliding": 0, "rate_per_second": 0}
        now = time.time()
        return {
            "fixed": counter.get_fixed(now),
            "sliding": round(counter.get_sliding(now), 1),
            "rate_per_second": counter.rate_per_second(now),
        }

    def get_all_resolutions(self, metric: str) -> dict[str, dict]:
        return {name: self.get(metric, name)
                for name in self._counters.get(metric, {})}

    def top_k(self, metric: str, k: int = 10) -> list[tuple[str, int]]:
        counts = self._top_k.get(metric, {})
        return sorted(counts.items(), key=lambda x: -x[1])[:k]

    def compare(self, metric_a: str, metric_b: str,
                resolution: str = "1m") -> dict:
        a = self.get(metric_a, resolution)
        b = self.get(metric_b, resolution)
        return {"a": a, "b": b,
                "ratio": round(a["sliding"] / max(0.001, b["sliding"]), 2)}

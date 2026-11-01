"""API performance profiler — profile endpoint performance and identify bottlenecks."""
from __future__ import annotations
from collections import defaultdict
import math


class PerfProfiler:
    def __init__(self):
        self._profiles: dict[str, list[float]] = defaultdict(list)

    def record(self, endpoint: str, latency_ms: float) -> dict:
        self._profiles[endpoint].append(latency_ms)
        return {"endpoint": endpoint, "recorded": True}

    def profile(self, endpoint: str) -> dict:
        values = self._profiles.get(endpoint, [])
        if not values:
            return {"endpoint": endpoint, "samples": 0}
        s = sorted(values)
        n = len(s)
        avg = round(sum(s) / n, 1)
        std = round(math.sqrt(sum((x - avg) ** 2 for x in s) / n), 1)
        return {"endpoint": endpoint, "samples": n, "min": s[0], "max": s[-1],
                "avg": avg, "std": std,
                "p50": s[n // 2], "p90": s[int(n * 0.9)],
                "p95": s[int(n * 0.95)], "p99": s[int(n * 0.99)]}

    def bottlenecks(self, threshold_ms: float = 200) -> list[dict]:
        results = []
        for ep in sorted(self._profiles):
            p = self.profile(ep)
            if p.get("p95", 0) > threshold_ms:
                results.append({"endpoint": ep, "p95": p["p95"], "avg": p["avg"]})
        return sorted(results, key=lambda r: -r["p95"])

    def summary(self) -> dict:
        return {"endpoints_profiled": len(self._profiles),
                "total_samples": sum(len(v) for v in self._profiles.values())}

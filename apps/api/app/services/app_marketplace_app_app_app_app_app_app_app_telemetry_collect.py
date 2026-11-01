"""Platform telemetry collector — collect, aggregate, and export telemetry."""
from __future__ import annotations
from collections import defaultdict
import time


class TelemetryCollector:
    def __init__(self, flush_interval: int = 60):
        self._flush_interval = flush_interval
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._last_flush = time.time()

    def increment(self, name: str, value: int = 1, tags: dict | None = None) -> dict:
        key = self._tagged_key(name, tags)
        self._counters[key] += value
        return {"metric": name, "type": "counter", "value": self._counters[key]}

    def gauge(self, name: str, value: float, tags: dict | None = None) -> dict:
        key = self._tagged_key(name, tags)
        self._gauges[key] = value
        return {"metric": name, "type": "gauge", "value": value}

    def histogram(self, name: str, value: float, tags: dict | None = None) -> dict:
        key = self._tagged_key(name, tags)
        self._histograms[key].append(value)
        return {"metric": name, "type": "histogram", "count": len(self._histograms[key])}

    def _tagged_key(self, name: str, tags: dict | None) -> str:
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"

    def snapshot(self) -> dict:
        hist_stats = {}
        for key, values in self._histograms.items():
            s = sorted(values)
            n = len(s)
            hist_stats[key] = {
                "count": n, "min": s[0] if s else 0, "max": s[-1] if s else 0,
                "avg": round(sum(s) / n, 2) if n else 0,
                "p50": s[n // 2] if n else 0,
                "p95": s[int(n * 0.95)] if n else 0,
                "p99": s[int(n * 0.99)] if n else 0,
            }
        return {"counters": dict(self._counters), "gauges": dict(self._gauges),
                "histograms": hist_stats,
                "total_metrics": len(self._counters) + len(self._gauges) + len(self._histograms)}

    def reset(self) -> dict:
        count = len(self._counters) + len(self._gauges) + len(self._histograms)
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._last_flush = time.time()
        return {"flushed": count}

"""API Latency Heatmap — time-bucket latency distribution visualization."""
from __future__ import annotations

import math
import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

LATENCY_BUCKETS = [0, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]


@dataclass
class LatencySample:
    endpoint_id: str
    time_bucket: str  # e.g. "2024-01-15T14:00"
    latency_ms: float


@dataclass
class LatencyHeatmap:
    """Build latency distribution heatmaps across time buckets."""

    _samples: dict[str, list[LatencySample]] = field(default_factory=dict)

    def record(self, sample: LatencySample) -> dict:
        if sample.latency_ms < 0:
            raise ValueError("Latency must be non-negative")
        self._samples.setdefault(sample.endpoint_id, []).append(sample)
        return {"endpoint_id": sample.endpoint_id,
                "total_samples": len(self._samples[sample.endpoint_id])}

    def _bucket_label(self, latency_ms: float) -> str:
        for i in range(len(LATENCY_BUCKETS) - 1):
            if latency_ms < LATENCY_BUCKETS[i + 1]:
                return f"{LATENCY_BUCKETS[i]}-{LATENCY_BUCKETS[i+1]}ms"
        return f"{LATENCY_BUCKETS[-1]}ms+"

    def get_heatmap(self, endpoint_id: str) -> dict:
        samples = self._samples.get(endpoint_id, [])
        if not samples:
            return {"endpoint_id": endpoint_id, "data": {}}
        heatmap: dict[str, dict[str, int]] = {}
        for s in samples:
            bucket = self._bucket_label(s.latency_ms)
            row = heatmap.setdefault(s.time_bucket, {})
            row[bucket] = row.get(bucket, 0) + 1
        return {"endpoint_id": endpoint_id, "data": heatmap,
                "time_buckets": sorted(heatmap.keys()),
                "latency_buckets": list({self._bucket_label(s.latency_ms) for s in samples})}

    def get_percentiles(self, endpoint_id: str) -> dict:
        samples = self._samples.get(endpoint_id, [])
        if not samples:
            return {"endpoint_id": endpoint_id, "status": "no_data"}
        values = sorted(s.latency_ms for s in samples)
        n = len(values)
        return {
            "endpoint_id": endpoint_id,
            "count": n,
            "min": values[0],
            "max": values[-1],
            "mean": round(statistics.mean(values), 2),
            "median": round(statistics.median(values), 2),
            "p90": round(values[int(n * 0.9)], 2) if n > 1 else values[0],
            "p95": round(values[int(n * 0.95)], 2) if n > 1 else values[0],
            "p99": round(values[min(int(n * 0.99), n - 1)], 2),
        }

    def get_hot_spots(self, endpoint_id: str, threshold_ms: float = 500) -> list[dict]:
        samples = self._samples.get(endpoint_id, [])
        bucket_counts: dict[str, list[float]] = {}
        for s in samples:
            bucket_counts.setdefault(s.time_bucket, []).append(s.latency_ms)
        hot_spots = []
        for tb, latencies in bucket_counts.items():
            avg = statistics.mean(latencies)
            if avg > threshold_ms:
                hot_spots.append({
                    "time_bucket": tb,
                    "avg_latency_ms": round(avg, 2),
                    "sample_count": len(latencies),
                    "max_latency_ms": max(latencies),
                })
        hot_spots.sort(key=lambda x: x["avg_latency_ms"], reverse=True)
        return hot_spots

    def compare_endpoints(self, endpoint_ids: list[str]) -> list[dict]:
        results = []
        for eid in endpoint_ids:
            perc = self.get_percentiles(eid)
            if perc.get("status") != "no_data":
                results.append(perc)
        results.sort(key=lambda x: x.get("p95", 0))
        return results

    def get_summary(self) -> dict:
        return {
            "endpoints": len(self._samples),
            "total_samples": sum(len(v) for v in self._samples.values()),
        }

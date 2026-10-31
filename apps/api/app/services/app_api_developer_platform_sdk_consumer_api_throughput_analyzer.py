"""Throughput Analyzer — measure and forecast API throughput capacity."""
from __future__ import annotations

import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ThroughputSample:
    endpoint_id: str
    timestamp: str
    requests_per_second: float
    avg_latency_ms: float
    error_count: int = 0


@dataclass
class ThroughputAnalyzer:
    """Analyze API throughput patterns and forecast capacity limits."""

    _samples: dict[str, list[ThroughputSample]] = field(default_factory=dict)

    def record(self, sample: ThroughputSample) -> dict:
        if sample.requests_per_second < 0:
            raise ValueError("requests_per_second must be non-negative")
        if sample.avg_latency_ms < 0:
            raise ValueError("avg_latency_ms must be non-negative")
        self._samples.setdefault(sample.endpoint_id, []).append(sample)
        logger.info("throughput_sample_recorded", endpoint_id=sample.endpoint_id,
                     rps=sample.requests_per_second)
        return {"endpoint_id": sample.endpoint_id, "total_samples": len(self._samples[sample.endpoint_id])}

    def analyze(self, endpoint_id: str) -> dict:
        samples = self._samples.get(endpoint_id, [])
        if not samples:
            return {"endpoint_id": endpoint_id, "status": "no_data"}
        rps_values = [s.requests_per_second for s in samples]
        latency_values = [s.avg_latency_ms for s in samples]
        error_counts = [s.error_count for s in samples]
        peak_rps = max(rps_values)
        avg_rps = statistics.mean(rps_values)
        avg_latency = statistics.mean(latency_values)
        total_errors = sum(error_counts)
        total_requests = sum(rps_values)
        error_rate = total_errors / total_requests if total_requests > 0 else 0.0
        median_rps = statistics.median(rps_values)
        # Capacity assessment
        if avg_latency > 500:
            capacity_status = "overloaded"
        elif avg_latency > 200:
            capacity_status = "stressed"
        elif len(rps_values) > 1 and median_rps > 0 and peak_rps > median_rps * 3:
            capacity_status = "spiky"
        else:
            capacity_status = "healthy"
        return {
            "endpoint_id": endpoint_id,
            "sample_count": len(samples),
            "peak_rps": peak_rps,
            "avg_rps": round(avg_rps, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "total_errors": total_errors,
            "error_rate": round(error_rate, 4),
            "capacity_status": capacity_status,
        }

    def forecast(self, endpoint_id: str, growth_rate: float = 0.1) -> dict:
        analysis = self.analyze(endpoint_id)
        if analysis.get("status") == "no_data":
            return {"endpoint_id": endpoint_id, "forecast": "insufficient_data"}
        avg_rps = analysis["avg_rps"]
        peak_rps = analysis["peak_rps"]
        if peak_rps == 0:
            return {"endpoint_id": endpoint_id, "forecast": "no_traffic"}
        estimated_capacity = peak_rps * 2
        if growth_rate <= 0:
            return {
                "endpoint_id": endpoint_id,
                "estimated_capacity_rps": round(estimated_capacity, 2),
                "forecast": "no_growth",
            }
        periods_to_limit = 0
        current = avg_rps
        while current < estimated_capacity and periods_to_limit < 100:
            current *= (1 + growth_rate)
            periods_to_limit += 1
        return {
            "endpoint_id": endpoint_id,
            "current_avg_rps": avg_rps,
            "estimated_capacity_rps": round(estimated_capacity, 2),
            "growth_rate": growth_rate,
            "periods_to_capacity": periods_to_limit,
        }

    def compare(self, endpoint_ids: list[str]) -> list[dict]:
        results = []
        for eid in endpoint_ids:
            analysis = self.analyze(eid)
            if analysis.get("status") != "no_data":
                results.append(analysis)
        results.sort(key=lambda x: x["avg_rps"], reverse=True)
        for i, r in enumerate(results):
            r["rank"] = i + 1
        return results

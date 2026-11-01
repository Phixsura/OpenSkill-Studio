"""Consumer API Endpoint Benchmark — endpoint performance benchmarking."""
from __future__ import annotations

import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class BenchmarkRun:
    run_id: str
    endpoint_id: str
    total_requests: int
    duration_seconds: float
    latencies_ms: list[float] = field(default_factory=list)
    errors: int = 0
    timestamp: str = ""


@dataclass
class EndpointBenchmark:
    """Benchmark API endpoint performance with comparison."""

    _runs: dict[str, BenchmarkRun] = field(default_factory=dict)

    def run(self, benchmark: BenchmarkRun) -> dict:
        if benchmark.run_id in self._runs:
            raise ValueError(f"Run {benchmark.run_id} already exists")
        if not benchmark.latencies_ms:
            raise ValueError("Latencies data required")
        self._runs[benchmark.run_id] = benchmark
        latencies = sorted(benchmark.latencies_ms)
        n = len(latencies)
        rps = benchmark.total_requests / benchmark.duration_seconds if benchmark.duration_seconds > 0 else 0
        logger.info("benchmark_completed", run_id=benchmark.run_id, rps=round(rps, 1))
        return {
            "run_id": benchmark.run_id,
            "endpoint_id": benchmark.endpoint_id,
            "rps": round(rps, 1),
            "avg_ms": round(statistics.mean(latencies), 2),
            "p50_ms": round(latencies[n // 2], 2),
            "p95_ms": round(latencies[int(n * 0.95)], 2) if n > 1 else latencies[0],
            "p99_ms": round(latencies[min(int(n * 0.99), n - 1)], 2),
            "min_ms": latencies[0],
            "max_ms": latencies[-1],
            "error_rate": round(benchmark.errors / benchmark.total_requests * 100, 2) if benchmark.total_requests > 0 else 0,
        }

    def compare(self, run_id_a: str, run_id_b: str) -> dict:
        a = self._runs.get(run_id_a)
        b = self._runs.get(run_id_b)
        if not a or not b:
            raise ValueError("Both runs must exist")
        avg_a = statistics.mean(a.latencies_ms)
        avg_b = statistics.mean(b.latencies_ms)
        rps_a = a.total_requests / a.duration_seconds if a.duration_seconds > 0 else 0
        rps_b = b.total_requests / b.duration_seconds if b.duration_seconds > 0 else 0
        latency_change = round((avg_b - avg_a) / avg_a * 100, 1) if avg_a > 0 else 0
        rps_change = round((rps_b - rps_a) / rps_a * 100, 1) if rps_a > 0 else 0
        return {
            "run_a": run_id_a, "run_b": run_id_b,
            "avg_latency_a": round(avg_a, 2), "avg_latency_b": round(avg_b, 2),
            "latency_change_pct": latency_change,
            "rps_a": round(rps_a, 1), "rps_b": round(rps_b, 1),
            "rps_change_pct": rps_change,
            "improved": latency_change < 0 or rps_change > 0,
        }

    def get_run(self, run_id: str) -> dict | None:
        r = self._runs.get(run_id)
        if not r:
            return None
        return self.run.__func__(self, BenchmarkRun(
            r.run_id, r.endpoint_id, r.total_requests,
            r.duration_seconds, list(r.latencies_ms), r.errors,
        ))

    def list_runs(self, endpoint_id: str | None = None) -> list[dict]:
        runs = list(self._runs.values())
        if endpoint_id:
            runs = [r for r in runs if r.endpoint_id == endpoint_id]
        return [{"run_id": r.run_id, "endpoint_id": r.endpoint_id,
                 "total_requests": r.total_requests, "errors": r.errors}
                for r in runs]

    def get_stats(self) -> dict:
        return {
            "total_runs": len(self._runs),
            "endpoints_benchmarked": len(set(r.endpoint_id for r in self._runs.values())),
            "total_requests": sum(r.total_requests for r in self._runs.values()),
        }

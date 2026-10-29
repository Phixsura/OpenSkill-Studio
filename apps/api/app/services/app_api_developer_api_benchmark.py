"""App API Developer API Benchmark — run and store API performance benchmarks."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class BenchmarkResult:
    benchmark_id: str
    endpoint: str
    rps: float  # requests per second
    avg_latency_ms: float
    p99_latency_ms: float
    error_rate: float = 0.0

class AppAPIDeveloperAPIBenchmark:
    def __init__(self) -> None:
        self._results: dict[tuple[str, str], BenchmarkResult] = {}

    def record(self, installation_id: str, benchmark_id: str, endpoint: str, rps: float, avg_latency_ms: float, p99_latency_ms: float, error_rate: float = 0.0) -> BenchmarkResult:
        if not installation_id: raise ValueError("installation_id is required")
        r = BenchmarkResult(benchmark_id=benchmark_id, endpoint=endpoint, rps=rps, avg_latency_ms=avg_latency_ms, p99_latency_ms=p99_latency_ms, error_rate=error_rate)
        self._results[(installation_id, benchmark_id)] = r
        return r

    def best_rps(self, installation_id: str, limit: int = 5) -> list[BenchmarkResult]:
        results = [r for (inst, _), r in self._results.items() if inst == installation_id]
        return sorted(results, key=lambda r: r.rps, reverse=True)[:limit]

    def slowest(self, installation_id: str, limit: int = 5) -> list[BenchmarkResult]:
        results = [r for (inst, _), r in self._results.items() if inst == installation_id]
        return sorted(results, key=lambda r: r.p99_latency_ms, reverse=True)[:limit]

    def list_results(self, installation_id: str) -> list[BenchmarkResult]:
        return [r for (inst, _), r in self._results.items() if inst == installation_id]

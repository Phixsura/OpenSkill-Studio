"""Consumer API Benchmark — run and track API performance benchmarks."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class BenchmarkConfig:
    benchmark_id: str
    endpoint_path: str
    method: str = "GET"
    concurrency: int = 10
    total_requests: int = 100
    timeout_ms: int = 5000

@dataclass
class BenchmarkResult:
    benchmark_id: str
    endpoint_path: str
    total_requests: int
    successful: int
    failed: int
    avg_latency_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    requests_per_second: float
    run_at: datetime

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark:
    def __init__(self) -> None:
        self._results: dict[tuple[str, str, str], list[BenchmarkResult]] = {}  # (inst, consumer, benchmark_id)

    def run(self, installation_id: str, consumer_id: str, config: BenchmarkConfig, now: datetime) -> BenchmarkResult:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.concurrency < 1:
            raise ValueError("concurrency must be positive")
        if config.total_requests < 1:
            raise ValueError("total_requests must be positive")
        # Simulated benchmark results
        import random
        base = random.uniform(20, 200)
        result = BenchmarkResult(
            benchmark_id=config.benchmark_id, endpoint_path=config.endpoint_path,
            total_requests=config.total_requests, successful=config.total_requests - random.randint(0, 2),
            failed=random.randint(0, 2), avg_latency_ms=round(base, 1),
            p50_ms=round(base * 0.8, 1), p95_ms=round(base * 2.5, 1), p99_ms=round(base * 4, 1),
            requests_per_second=round(config.total_requests / (base * config.total_requests / 1000 / config.concurrency), 1),
            run_at=now,
        )
        key = (installation_id, consumer_id, config.benchmark_id)
        if key not in self._results:
            self._results[key] = []
        self._results[key].append(result)
        log.info("benchmark_completed", installation_id=installation_id, consumer=consumer_id, rps=result.requests_per_second)
        return result

    def get_history(self, installation_id: str, consumer_id: str, benchmark_id: str, limit: int = 10) -> list[BenchmarkResult]:
        return self._results.get((installation_id, consumer_id, benchmark_id), [])[-limit:]

    def compare_latest(self, installation_id: str, consumer_id: str, benchmark_id: str) -> dict[str, float] | None:
        results = self._results.get((installation_id, consumer_id, benchmark_id), [])
        if len(results) < 2:
            return None
        prev, curr = results[-2], results[-1]
        return {
            "latency_change_pct": round((curr.avg_latency_ms - prev.avg_latency_ms) / max(prev.avg_latency_ms, 0.01) * 100, 1),
            "rps_change_pct": round((curr.requests_per_second - prev.requests_per_second) / max(prev.requests_per_second, 0.01) * 100, 1),
        }

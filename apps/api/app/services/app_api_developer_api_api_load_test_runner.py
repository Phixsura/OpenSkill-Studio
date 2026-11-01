"""App API Developer API Load Test Runner — run and track load test results."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class LoadTestResult:
    test_id: str
    endpoint: str
    concurrency: int
    total_requests: int
    successful: int
    failed: int
    avg_latency_ms: float
    p99_latency_ms: float
    rps: float  # requests per second

    @property
    def success_rate(self) -> float:
        return round(self.successful / self.total_requests * 100, 1) if self.total_requests > 0 else 0.0

    @property
    def passed(self) -> bool:
        return self.success_rate >= 99.0 and self.p99_latency_ms <= 1000

class AppAPIDeveloperAPIApiLoadTestRunner:
    def __init__(self) -> None:
        self._results: dict[tuple[str, str], LoadTestResult] = {}

    def record(self, installation_id: str, test_id: str, endpoint: str, concurrency: int, total_requests: int, successful: int, failed: int, avg_latency_ms: float, p99_latency_ms: float, rps: float) -> LoadTestResult:
        if not installation_id: raise ValueError("installation_id is required")
        if concurrency < 1: raise ValueError("concurrency must be >= 1")
        r = LoadTestResult(test_id=test_id, endpoint=endpoint, concurrency=concurrency, total_requests=total_requests, successful=successful, failed=failed, avg_latency_ms=avg_latency_ms, p99_latency_ms=p99_latency_ms, rps=rps)
        self._results[(installation_id, test_id)] = r
        return r

    def get(self, installation_id: str, test_id: str) -> LoadTestResult:
        key = (installation_id, test_id)
        r = self._results.get(key)
        if r is None: raise KeyError(f"Test {test_id} not found")
        return r

    def failing_tests(self, installation_id: str) -> list[LoadTestResult]:
        return [r for (inst, _), r in self._results.items() if inst == installation_id and not r.passed]

    def all_results(self, installation_id: str) -> list[LoadTestResult]:
        return [r for (inst, _), r in self._results.items() if inst == installation_id]

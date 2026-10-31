"""Extension Benchmark Runner — performance benchmarks for extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import statistics


@dataclass
class BenchmarkResult:
    benchmark_id: str
    extension_id: str
    name: str
    samples: list[float] = field(default_factory=list)
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()

    @property
    def mean_ms(self) -> float:
        return round(statistics.mean(self.samples), 2) if self.samples else 0

    @property
    def p95_ms(self) -> float:
        if not self.samples: return 0
        sorted_s = sorted(self.samples)
        idx = int(len(sorted_s) * 0.95)
        return round(sorted_s[min(idx, len(sorted_s)-1)], 2)

    @property
    def p99_ms(self) -> float:
        if not self.samples: return 0
        sorted_s = sorted(self.samples)
        idx = int(len(sorted_s) * 0.99)
        return round(sorted_s[min(idx, len(sorted_s)-1)], 2)


class ExtBenchmarkRunnerService:
    def __init__(self):
        self._results: dict[str, list[BenchmarkResult]] = {}
        self._counter = 0

    def run(self, extension_id: str, name: str, samples: list[float]) -> BenchmarkResult:
        if not samples:
            raise ValueError("No samples provided")
        self._counter += 1
        result = BenchmarkResult(benchmark_id=f"bench-{self._counter}",
                                 extension_id=extension_id, name=name, samples=samples)
        if extension_id not in self._results:
            self._results[extension_id] = []
        self._results[extension_id].append(result)
        return result

    def get_results(self, extension_id: str) -> list[BenchmarkResult]:
        return self._results.get(extension_id, [])

    def compare(self, ext_a: str, ext_b: str, benchmark_name: str) -> dict | None:
        results_a = [r for r in self._results.get(ext_a, []) if r.name == benchmark_name]
        results_b = [r for r in self._results.get(ext_b, []) if r.name == benchmark_name]
        if not results_a or not results_b:
            return None
        a, b = results_a[-1], results_b[-1]
        return {"benchmark": benchmark_name,
                "a": {"ext": ext_a, "mean": a.mean_ms, "p95": a.p95_ms},
                "b": {"ext": ext_b, "mean": b.mean_ms, "p95": b.p95_ms},
                "faster": ext_a if a.mean_ms < b.mean_ms else ext_b}

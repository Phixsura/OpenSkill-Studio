"""App API Developer Integration Test Runner — run and track integration test suites."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class TestCase:
    name: str
    status: str  # "passed", "failed", "skipped"
    duration_ms: float = 0.0
    error_message: str = ""

@dataclass
class TestSuiteRun:
    run_id: str
    suite_name: str
    cases: list[TestCase] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None

    @property
    def total(self) -> int: return len(self.cases)
    @property
    def passed(self) -> int: return sum(1 for c in self.cases if c.status == "passed")
    @property
    def failed(self) -> int: return sum(1 for c in self.cases if c.status == "failed")
    @property
    def pass_rate(self) -> float: return round(self.passed / self.total * 100, 1) if self.total > 0 else 0.0
    @property
    def all_passed(self) -> bool: return self.failed == 0 and self.total > 0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunner:
    def __init__(self) -> None:
        self._runs: dict[tuple[str, str], TestSuiteRun] = {}

    def start_run(self, installation_id: str, run_id: str, suite_name: str) -> TestSuiteRun:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, run_id)
        r = TestSuiteRun(run_id=run_id, suite_name=suite_name)
        self._runs[key] = r
        return r

    def add_result(self, installation_id: str, run_id: str, name: str, status: str, duration_ms: float = 0.0, error_message: str = "") -> TestSuiteRun:
        if status not in ("passed", "failed", "skipped"): raise ValueError("invalid status")
        key = (installation_id, run_id)
        r = self._runs.get(key)
        if r is None: raise KeyError(f"Run {run_id} not found")
        r.cases.append(TestCase(name=name, status=status, duration_ms=duration_ms, error_message=error_message))
        return r

    def complete_run(self, installation_id: str, run_id: str) -> TestSuiteRun:
        key = (installation_id, run_id)
        r = self._runs.get(key)
        if r is None: raise KeyError(f"Run {run_id} not found")
        r.completed_at = time.time()
        return r

    def recent_runs(self, installation_id: str, limit: int = 10) -> list[TestSuiteRun]:
        runs = [r for (inst, _), r in self._runs.items() if inst == installation_id]
        return sorted(runs, key=lambda r: r.started_at, reverse=True)[:limit]

    def failing_runs(self, installation_id: str) -> list[TestSuiteRun]:
        return [r for (inst, _), r in self._runs.items() if inst == installation_id and not r.all_passed and r.total > 0]

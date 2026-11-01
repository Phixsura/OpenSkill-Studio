"""API Consumer Test Suite — manage automated test suites for API integrations."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"

@dataclass
class TestCase:
    test_id: str
    name: str
    endpoint: str
    method: str
    expected_status: int
    passed: bool | None = None

@dataclass
class TestRun:
    run_id: str
    consumer_id: str
    status: RunStatus = RunStatus.QUEUED
    tests: list[TestCase] = field(default_factory=list)
    started_at: float = 0.0
    completed_at: float = 0.0
    pass_count: int = 0
    fail_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTestSuite:
    def __init__(self) -> None:
        self._runs: dict[tuple[str, str], TestRun] = {}

    def create_run(self, installation_id: str, run: TestRun) -> TestRun:
        if not installation_id: raise ValueError("installation_id is required")
        if not run.tests: raise ValueError("Test suite must have at least one test")
        key = (installation_id, run.run_id)
        if key in self._runs: raise ValueError(f"Run {run.run_id} exists")
        self._runs[key] = run
        return run

    def start_run(self, installation_id: str, run_id: str) -> TestRun:
        run = self._get(installation_id, run_id)
        run.status = RunStatus.RUNNING
        run.started_at = time.time()
        return run

    def record_result(self, installation_id: str, run_id: str, test_id: str, actual_status: int) -> TestRun:
        run = self._get(installation_id, run_id)
        for t in run.tests:
            if t.test_id == test_id:
                t.passed = actual_status == t.expected_status
                if t.passed: run.pass_count += 1
                else: run.fail_count += 1
                break
        all_done = all(t.passed is not None for t in run.tests)
        if all_done:
            run.status = RunStatus.PASSED if run.fail_count == 0 else RunStatus.FAILED
            run.completed_at = time.time()
        return run

    def get_run(self, installation_id: str, run_id: str) -> TestRun:
        return self._get(installation_id, run_id)

    def pass_rate(self, installation_id: str, run_id: str) -> float:
        run = self._get(installation_id, run_id)
        total = run.pass_count + run.fail_count
        if total == 0: return 0.0
        return round((run.pass_count / total) * 100, 1)

    def list_runs(self, installation_id: str) -> list[TestRun]:
        return [r for (inst, _), r in self._runs.items() if inst == installation_id]

    def _get(self, installation_id: str, run_id: str) -> TestRun:
        r = self._runs.get((installation_id, run_id))
        if r is None: raise KeyError(f"Run {run_id} not found")
        return r

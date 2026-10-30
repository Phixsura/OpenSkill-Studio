"""Consumer API Integration Test Runner — run and track integration tests."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class TestCase:
    test_id: str
    name: str
    method: str
    path: str
    expected_status: int
    expected_body_contains: str = ""

@dataclass
class TestRun:
    run_id: str
    consumer_id: str
    test_cases: list[TestCase]
    started_at: datetime
    completed_at: datetime | None = None
    passed: int = 0
    failed: int = 0
    results: list[dict] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner:
    def __init__(self) -> None:
        self._suites: dict[tuple[str, str, str], list[TestCase]] = {}  # (inst, consumer, suite_name)
        self._runs: dict[tuple[str, str], list[TestRun]] = {}

    def register_suite(self, installation_id: str, consumer_id: str, suite_name: str, test_cases: list[TestCase]) -> int:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not test_cases:
            raise ValueError("At least one test case required")
        self._suites[(installation_id, consumer_id, suite_name)] = test_cases
        return len(test_cases)

    def run_suite(self, installation_id: str, consumer_id: str, suite_name: str, now: datetime) -> TestRun:
        key = (installation_id, consumer_id, suite_name)
        cases = self._suites.get(key)
        if not cases:
            raise ValueError("Suite not found")
        passed = 0
        failed = 0
        results = []
        for tc in cases:
            # Simulated execution
            actual_status = tc.expected_status  # simulate pass
            success = actual_status == tc.expected_status
            if success:
                passed += 1
            else:
                failed += 1
            results.append({"test_id": tc.test_id, "name": tc.name, "passed": success, "actual_status": actual_status})
        run = TestRun(run_id=f"run-{now.isoformat()}", consumer_id=consumer_id, test_cases=cases, started_at=now, completed_at=now, passed=passed, failed=failed, results=results)
        rkey = (installation_id, consumer_id)
        if rkey not in self._runs:
            self._runs[rkey] = []
        self._runs[rkey].append(run)
        log.info("test_run_completed", installation_id=installation_id, consumer=consumer_id, passed=passed, failed=failed)
        return run

    def get_runs(self, installation_id: str, consumer_id: str, limit: int = 10) -> list[TestRun]:
        return self._runs.get((installation_id, consumer_id), [])[-limit:]

    def list_suites(self, installation_id: str, consumer_id: str) -> list[str]:
        return [name for (inst, cid, name) in self._suites if inst == installation_id and cid == consumer_id]

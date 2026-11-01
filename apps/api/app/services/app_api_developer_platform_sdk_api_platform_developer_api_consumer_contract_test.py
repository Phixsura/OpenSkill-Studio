"""API Consumer Contract Test — define and run contract tests for consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class TestResult(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ContractTest:
    test_id: str
    consumer_id: str
    endpoint: str
    method: str
    expected_status: int
    expected_fields: list[str] = field(default_factory=list)
    description: str = ""

@dataclass
class TestExecution:
    test_id: str
    result: TestResult
    actual_status: int = 0
    missing_fields: list[str] = field(default_factory=list)
    executed_at: float = field(default_factory=time.time)
    duration_ms: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTest:
    def __init__(self) -> None:
        self._tests: dict[tuple[str, str], list[ContractTest]] = {}
        self._executions: dict[tuple[str, str], list[TestExecution]] = {}

    def add_test(self, installation_id: str, test: ContractTest) -> ContractTest:
        if not installation_id: raise ValueError("installation_id is required")
        self._tests.setdefault((installation_id, test.consumer_id), []).append(test)
        return test

    def execute(self, installation_id: str, test_id: str, consumer_id: str, actual_status: int, response_fields: list[str], duration_ms: float = 0.0) -> TestExecution:
        tests = self._tests.get((installation_id, consumer_id), [])
        test = next((t for t in tests if t.test_id == test_id), None)
        if test is None: raise KeyError(f"Test {test_id} not found")
        missing = [f for f in test.expected_fields if f not in response_fields]
        status_ok = actual_status == test.expected_status
        result = TestResult.PASSED if status_ok and not missing else TestResult.FAILED
        ex = TestExecution(test_id=test_id, result=result, actual_status=actual_status, missing_fields=missing, duration_ms=duration_ms)
        self._executions.setdefault((installation_id, consumer_id), []).append(ex)
        return ex

    def pass_rate(self, installation_id: str, consumer_id: str) -> float:
        execs = self._executions.get((installation_id, consumer_id), [])
        if not execs: return 0.0
        passed = sum(1 for e in execs if e.result == TestResult.PASSED)
        return round((passed / len(execs)) * 100, 1)

    def list_tests(self, installation_id: str, consumer_id: str) -> list[ContractTest]:
        return self._tests.get((installation_id, consumer_id), [])

    def recent_executions(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[TestExecution]:
        return list(reversed(self._executions.get((installation_id, consumer_id), [])[-limit:]))

    def test_count(self, installation_id: str) -> int:
        return sum(len(ts) for (inst, _), ts in self._tests.items() if inst == installation_id)

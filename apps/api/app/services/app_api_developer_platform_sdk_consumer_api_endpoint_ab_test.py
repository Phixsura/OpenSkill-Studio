"""Consumer API Endpoint A/B Test — run A/B tests on API endpoint variants."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class ABTestVariant:
    variant_id: str
    name: str
    weight_pct: int  # 0-100
    endpoint_version: str

@dataclass
class ABTest:
    test_id: str
    endpoint_path: str
    variants: list[ABTestVariant] = field(default_factory=list)
    status: str = "draft"  # "draft", "running", "completed"
    created_at: datetime | None = None

@dataclass
class ABTestAssignment:
    consumer_id: str
    variant_id: str
    variant_name: str

@dataclass
class ABTestResult:
    test_id: str
    variant_id: str
    requests: int
    errors: int
    avg_latency_ms: float

class AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest:
    def __init__(self) -> None:
        self._tests: dict[tuple[str, str], ABTest] = {}
        self._results: dict[tuple[str, str, str], ABTestResult] = {}

    def create(self, installation_id: str, test: ABTest) -> ABTest:
        if not installation_id:
            raise ValueError("installation_id is required")
        total_weight = sum(v.weight_pct for v in test.variants)
        if test.variants and total_weight != 100:
            raise ValueError(f"Variant weights must sum to 100, got {total_weight}")
        test.created_at = test.created_at or datetime.utcnow()
        self._tests[(installation_id, test.test_id)] = test
        return test

    def start(self, installation_id: str, test_id: str) -> ABTest:
        key = (installation_id, test_id)
        test = self._tests.get(key)
        if not test:
            raise ValueError("Test not found")
        if not test.variants:
            raise ValueError("Test must have variants")
        test.status = "running"
        return test

    def assign(self, installation_id: str, test_id: str, consumer_id: str) -> ABTestAssignment:
        test = self._tests.get((installation_id, test_id))
        if not test or test.status != "running":
            raise ValueError("Test not running")
        # Deterministic assignment via hash
        h = int(hashlib.sha256(f"{installation_id}:{test_id}:{consumer_id}".encode()).hexdigest(), 16) % 100
        cumulative = 0
        for v in test.variants:
            cumulative += v.weight_pct
            if h < cumulative:
                return ABTestAssignment(consumer_id=consumer_id, variant_id=v.variant_id, variant_name=v.name)
        last = test.variants[-1]
        return ABTestAssignment(consumer_id=consumer_id, variant_id=last.variant_id, variant_name=last.name)

    def record_result(self, installation_id: str, result: ABTestResult) -> ABTestResult:
        self._results[(installation_id, result.test_id, result.variant_id)] = result
        return result

    def get_results(self, installation_id: str, test_id: str) -> list[ABTestResult]:
        return [r for (inst, tid, _), r in self._results.items() if inst == installation_id and tid == test_id]

    def list_tests(self, installation_id: str) -> list[ABTest]:
        return [t for (inst, _), t in self._tests.items() if inst == installation_id]

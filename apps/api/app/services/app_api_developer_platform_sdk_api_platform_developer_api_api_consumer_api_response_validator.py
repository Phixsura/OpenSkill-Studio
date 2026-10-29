"""API Consumer Response Validator — validate API responses match consumer expectations."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ResponseExpectation:
    endpoint: str
    method: str
    expected_status: int
    expected_content_type: str = "application/json"
    required_fields: list[str] = field(default_factory=list)
    max_latency_ms: float = 0  # 0 = no limit

@dataclass
class ValidationResult:
    endpoint: str
    passed: bool
    failures: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidator:
    def __init__(self) -> None:
        self._expectations: dict[tuple[str, str, str, str], ResponseExpectation] = {}
        self._results: dict[str, list[ValidationResult]] = {}

    def set_expectation(self, installation_id: str, consumer_id: str, exp: ResponseExpectation) -> ResponseExpectation:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, exp.method.upper(), exp.endpoint)
        exp.method = exp.method.upper()
        self._expectations[key] = exp
        return exp

    def validate(self, installation_id: str, consumer_id: str, method: str, endpoint: str, actual_status: int, actual_content_type: str = "", actual_fields: list[str] | None = None, latency_ms: float = 0) -> ValidationResult:
        key = (installation_id, consumer_id, method.upper(), endpoint)
        exp = self._expectations.get(key)
        if exp is None: return ValidationResult(endpoint=endpoint, passed=True)
        failures: list[str] = []
        if actual_status != exp.expected_status:
            failures.append(f"Status: expected {exp.expected_status}, got {actual_status}")
        if exp.expected_content_type and actual_content_type and exp.expected_content_type not in actual_content_type:
            failures.append(f"Content-Type: expected {exp.expected_content_type}")
        if actual_fields is not None:
            missing = [f for f in exp.required_fields if f not in actual_fields]
            if missing: failures.append(f"Missing fields: {', '.join(missing)}")
        if exp.max_latency_ms > 0 and latency_ms > exp.max_latency_ms:
            failures.append(f"Latency: {latency_ms}ms > {exp.max_latency_ms}ms")
        result = ValidationResult(endpoint=endpoint, passed=len(failures) == 0, failures=failures)
        self._results.setdefault(installation_id, []).append(result)
        return result

    def pass_rate(self, installation_id: str) -> float:
        results = self._results.get(installation_id, [])
        if not results: return 0.0
        return round(sum(1 for r in results if r.passed) / len(results) * 100, 1)

    def list_expectations(self, installation_id: str, consumer_id: str) -> list[ResponseExpectation]:
        return [e for (inst, cid, _, _), e in self._expectations.items() if inst == installation_id and cid == consumer_id]

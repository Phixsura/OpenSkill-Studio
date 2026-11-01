"""App API Developer API Health Check — developer-facing health check summary."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class HealthCheckResult:
    check_name: str
    status: str  # "pass", "fail", "warn"
    message: str = ""
    duration_ms: float = 0.0

class AppAPIDeveloperAPIHealthCheck:
    def __init__(self) -> None:
        self._checks: dict[str, list[HealthCheckResult]] = {}

    def run_check(self, installation_id: str, check_name: str, status: str, message: str = "", duration_ms: float = 0.0) -> HealthCheckResult:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("pass", "fail", "warn"): raise ValueError("status must be pass, fail, or warn")
        r = HealthCheckResult(check_name=check_name, status=status, message=message, duration_ms=duration_ms)
        self._checks.setdefault(installation_id, []).append(r)
        return r

    def latest_results(self, installation_id: str) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}
        for r in self._checks.get(installation_id, []):
            results[r.check_name] = r
        return results

    def all_passing(self, installation_id: str) -> bool:
        results = self.latest_results(installation_id)
        return all(r.status == "pass" for r in results.values()) if results else True

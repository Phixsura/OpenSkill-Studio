"""App API Developer Endpoint Error Rate Monitor — real-time error rate per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointErrorRate:
    endpoint: str
    total_requests: int = 0
    error_count: int = 0
    last_error_code: str = ""

    @property
    def error_rate_pct(self) -> float:
        return round(self.error_count / self.total_requests * 100, 2) if self.total_requests > 0 else 0.0

    @property
    def status(self) -> str:
        r = self.error_rate_pct
        if r >= 10: return "critical"
        if r >= 5: return "warning"
        if r >= 1: return "elevated"
        return "normal"

class AppAPIDeveloperPlatformSDKApiEndpointErrorRateMonitor:
    def __init__(self) -> None:
        self._rates: dict[tuple[str, str], EndpointErrorRate] = {}

    def record(self, installation_id: str, endpoint: str, success: bool, error_code: str = "") -> EndpointErrorRate:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        if key not in self._rates:
            self._rates[key] = EndpointErrorRate(endpoint=endpoint)
        r = self._rates[key]
        r.total_requests += 1
        if not success:
            r.error_count += 1
            r.last_error_code = error_code
        return r

    def critical_endpoints(self, installation_id: str) -> list[EndpointErrorRate]:
        return [r for (inst, _), r in self._rates.items() if inst == installation_id and r.status == "critical"]

    def all_endpoints(self, installation_id: str) -> list[EndpointErrorRate]:
        return sorted([r for (inst, _), r in self._rates.items() if inst == installation_id], key=lambda r: r.error_rate_pct, reverse=True)

    def overall_error_rate(self, installation_id: str) -> float:
        endpoints = [r for (inst, _), r in self._rates.items() if inst == installation_id]
        total = sum(r.total_requests for r in endpoints)
        errors = sum(r.error_count for r in endpoints)
        return round(errors / total * 100, 2) if total > 0 else 0.0

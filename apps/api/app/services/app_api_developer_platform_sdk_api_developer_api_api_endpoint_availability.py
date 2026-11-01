"""App API Developer API Endpoint Availability — track endpoint availability windows."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointAvailability:
    endpoint: str
    total_checks: int = 0
    available_checks: int = 0
    current_status: str = "up"  # "up", "down", "degraded"

    @property
    def availability_pct(self) -> float:
        return round(self.available_checks / self.total_checks * 100, 3) if self.total_checks > 0 else 100.0

    @property
    def nines(self) -> str:
        a = self.availability_pct
        if a >= 99.999: return "5 nines"
        if a >= 99.99: return "4 nines"
        if a >= 99.9: return "3 nines"
        if a >= 99: return "2 nines"
        return "< 2 nines"

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointAvailability:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], EndpointAvailability] = {}

    def check(self, installation_id: str, endpoint: str, available: bool) -> EndpointAvailability:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        if key not in self._endpoints:
            self._endpoints[key] = EndpointAvailability(endpoint=endpoint)
        e = self._endpoints[key]
        e.total_checks += 1
        if available:
            e.available_checks += 1
            e.current_status = "up"
        else:
            e.current_status = "down"
        return e

    def below_target(self, installation_id: str, target_pct: float = 99.9) -> list[EndpointAvailability]:
        return [e for (inst, _), e in self._endpoints.items() if inst == installation_id and e.availability_pct < target_pct]

    def all_endpoints(self, installation_id: str) -> list[EndpointAvailability]:
        return [e for (inst, _), e in self._endpoints.items() if inst == installation_id]

    def overall_availability(self, installation_id: str) -> float:
        endpoints = self.all_endpoints(installation_id)
        if not endpoints: return 100.0
        total_c = sum(e.total_checks for e in endpoints)
        avail_c = sum(e.available_checks for e in endpoints)
        return round(avail_c / total_c * 100, 3) if total_c > 0 else 100.0

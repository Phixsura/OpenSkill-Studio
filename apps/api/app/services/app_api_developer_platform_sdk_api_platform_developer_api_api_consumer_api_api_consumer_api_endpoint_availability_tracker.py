"""API Consumer Endpoint Availability Tracker — track real-time endpoint availability."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class AvailabilityWindow:
    endpoint: str
    method: str
    total_checks: int = 0
    successful_checks: int = 0
    current_streak: int = 0  # consecutive successes
    longest_downtime_checks: int = 0

    @property
    def availability_pct(self) -> float:
        if self.total_checks == 0: return 100.0
        return round((self.successful_checks / self.total_checks) * 100, 3)

    @property
    def is_up(self) -> bool:
        return self.current_streak > 0 or self.total_checks == 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTracker:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str, str], AvailabilityWindow] = {}

    def record_check(self, installation_id: str, endpoint: str, method: str, success: bool) -> AvailabilityWindow:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        w = self._windows.get(key)
        if w is None:
            w = AvailabilityWindow(endpoint=endpoint, method=method.upper())
            self._windows[key] = w
        w.total_checks += 1
        if success:
            w.successful_checks += 1
            w.current_streak += 1
        else:
            if w.current_streak == 0:
                w.longest_downtime_checks += 1
            w.current_streak = 0

    def down_endpoints(self, installation_id: str) -> list[AvailabilityWindow]:
        return [w for (inst, _, _), w in self._windows.items() if inst == installation_id and not w.is_up]

    def below_sla(self, installation_id: str, sla_pct: float = 99.9) -> list[AvailabilityWindow]:
        return [w for (inst, _, _), w in self._windows.items() if inst == installation_id and w.availability_pct < sla_pct and w.total_checks > 0]

    def list_windows(self, installation_id: str) -> list[AvailabilityWindow]:
        return [w for (inst, _, _), w in self._windows.items() if inst == installation_id]

"""Consumer API Endpoint SLA Monitor — track per-endpoint SLA compliance."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class SLATarget:
    endpoint_path: str
    availability_pct: float = 99.9
    latency_p99_ms: float = 500
    error_rate_max_pct: float = 0.1

@dataclass
class SLAMeasurement:
    endpoint_path: str
    timestamp: datetime
    availability_pct: float
    latency_p99_ms: float
    error_rate_pct: float
    request_count: int

@dataclass
class SLAComplianceReport:
    endpoint_path: str
    in_compliance: bool
    availability_ok: bool
    latency_ok: bool
    error_rate_ok: bool
    current_availability: float
    current_latency_p99: float
    current_error_rate: float

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor:
    def __init__(self) -> None:
        self._targets: dict[tuple[str, str], SLATarget] = {}
        self._measurements: dict[tuple[str, str], list[SLAMeasurement]] = {}

    def set_target(self, installation_id: str, target: SLATarget) -> SLATarget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0 < target.availability_pct <= 100):
            raise ValueError("availability_pct must be 0-100")
        self._targets[(installation_id, target.endpoint_path)] = target
        return target

    def record(self, installation_id: str, measurement: SLAMeasurement) -> SLAMeasurement:
        key = (installation_id, measurement.endpoint_path)
        if key not in self._measurements:
            self._measurements[key] = []
        self._measurements[key].append(measurement)
        if len(self._measurements[key]) > 1000:
            self._measurements[key] = self._measurements[key][-1000:]
        return measurement

    def check_compliance(self, installation_id: str, endpoint_path: str) -> SLAComplianceReport:
        target = self._targets.get((installation_id, endpoint_path))
        measurements = self._measurements.get((installation_id, endpoint_path), [])
        if not target or not measurements:
            return SLAComplianceReport(endpoint_path=endpoint_path, in_compliance=True, availability_ok=True, latency_ok=True, error_rate_ok=True, current_availability=100, current_latency_p99=0, current_error_rate=0)
        avg_avail = sum(m.availability_pct for m in measurements) / len(measurements)
        avg_latency = sum(m.latency_p99_ms for m in measurements) / len(measurements)
        avg_errors = sum(m.error_rate_pct for m in measurements) / len(measurements)
        avail_ok = avg_avail >= target.availability_pct
        lat_ok = avg_latency <= target.latency_p99_ms
        err_ok = avg_errors <= target.error_rate_max_pct
        return SLAComplianceReport(endpoint_path=endpoint_path, in_compliance=avail_ok and lat_ok and err_ok, availability_ok=avail_ok, latency_ok=lat_ok, error_rate_ok=err_ok, current_availability=round(avg_avail, 2), current_latency_p99=round(avg_latency, 1), current_error_rate=round(avg_errors, 3))

    def list_targets(self, installation_id: str) -> list[SLATarget]:
        return [t for (inst, _), t in self._targets.items() if inst == installation_id]

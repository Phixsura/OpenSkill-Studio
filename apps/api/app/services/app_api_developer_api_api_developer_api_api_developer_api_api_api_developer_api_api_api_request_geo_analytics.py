"""App API Developer Request Geo Analytics — geographic request distribution analytics."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GeoRegion:
    region: str  # "NA", "EU", "APAC", "LATAM", "MEA"
    request_count: int = 0
    avg_latency_ms: float = 0.0
    error_count: int = 0

    @property
    def error_rate(self) -> float:
        return round(self.error_count / self.request_count * 100, 1) if self.request_count > 0 else 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalytics:
    def __init__(self) -> None:
        self._regions: dict[tuple[str, str], GeoRegion] = {}

    def record(self, installation_id: str, region: str, requests: int, avg_latency_ms: float, errors: int = 0) -> GeoRegion:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"NA", "EU", "APAC", "LATAM", "MEA"}
        if region not in valid: raise ValueError(f"Invalid region: {region}")
        key = (installation_id, region)
        if key not in self._regions:
            self._regions[key] = GeoRegion(region=region)
        r = self._regions[key]
        r.request_count += requests
        r.error_count += errors
        # running avg
        if r.request_count > 0:
            r.avg_latency_ms = round(((r.avg_latency_ms * (r.request_count - requests)) + avg_latency_ms * requests) / r.request_count, 1)
        return r

    def distribution(self, installation_id: str) -> list[GeoRegion]:
        regions = [r for (inst, _), r in self._regions.items() if inst == installation_id]
        return sorted(regions, key=lambda r: r.request_count, reverse=True)

    def slowest_region(self, installation_id: str) -> GeoRegion | None:
        regions = self.distribution(installation_id)
        return max(regions, key=lambda r: r.avg_latency_ms) if regions else None

    def total_requests(self, installation_id: str) -> int:
        return sum(r.request_count for (inst, _), r in self._regions.items() if inst == installation_id)

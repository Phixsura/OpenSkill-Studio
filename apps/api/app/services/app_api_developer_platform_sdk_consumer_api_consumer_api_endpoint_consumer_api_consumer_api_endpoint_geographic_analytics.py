"""Consumer API Endpoint Geographic Analytics — analyze request origins by region."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GeoRecord:
    country_code: str
    region: str  # "NA", "EU", "APAC", "LATAM", "MEA"
    request_count: int = 0
    avg_latency_ms: float = 0.0
    error_count: int = 0

@dataclass
class GeoAnalytics:
    total_requests: int
    unique_countries: int
    by_region: dict[str, int]
    top_countries: list[GeoRecord]
    highest_latency_country: str
    highest_error_country: str

VALID_REGIONS = {"NA", "EU", "APAC", "LATAM", "MEA", "OTHER"}

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], list[GeoRecord]] = {}

    def record(self, installation_id: str, consumer_id: str, geo: GeoRecord) -> GeoRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        if geo.region not in VALID_REGIONS:
            raise ValueError(f"Invalid region: {geo.region}")
        key = (installation_id, consumer_id)
        if key not in self._records:
            self._records[key] = []
        # Update existing or add
        for existing in self._records[key]:
            if existing.country_code == geo.country_code:
                existing.request_count += geo.request_count
                n = existing.request_count
                existing.avg_latency_ms = existing.avg_latency_ms + (geo.avg_latency_ms - existing.avg_latency_ms) * geo.request_count / n
                existing.error_count += geo.error_count
                return existing
        self._records[key].append(geo)
        return geo

    def analyze(self, installation_id: str, consumer_id: str) -> GeoAnalytics:
        records = self._records.get((installation_id, consumer_id), [])
        if not records:
            return GeoAnalytics(total_requests=0, unique_countries=0, by_region={}, top_countries=[], highest_latency_country="", highest_error_country="")
        total = sum(r.request_count for r in records)
        by_region: dict[str, int] = {}
        for r in records:
            by_region[r.region] = by_region.get(r.region, 0) + r.request_count
        top = sorted(records, key=lambda r: -r.request_count)[:10]
        high_lat = max(records, key=lambda r: r.avg_latency_ms).country_code if records else ""
        high_err = max(records, key=lambda r: r.error_count).country_code if records else ""
        return GeoAnalytics(total_requests=total, unique_countries=len(records), by_region=by_region, top_countries=top, highest_latency_country=high_lat, highest_error_country=high_err)

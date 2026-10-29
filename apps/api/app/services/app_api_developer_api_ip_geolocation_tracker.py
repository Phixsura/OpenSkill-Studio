"""App API Developer IP Geolocation Tracker — geographic distribution of API traffic."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GeoStats:
    country: str
    region: str = ""
    request_count: int = 0
    unique_ips: set[str] = field(default_factory=set)
    error_count: int = 0

class AppAPIDeveloperAPIIPGeolocationTracker:
    def __init__(self) -> None:
        self._stats: dict[tuple[str, str], GeoStats] = {}

    def track(self, installation_id: str, ip_address: str, country: str, region: str = "", success: bool = True) -> GeoStats:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, country)
        if key not in self._stats:
            self._stats[key] = GeoStats(country=country, region=region)
        g = self._stats[key]
        g.request_count += 1
        g.unique_ips.add(ip_address)
        if not success: g.error_count += 1
        return g

    def top_countries(self, installation_id: str, limit: int = 10) -> list[GeoStats]:
        stats = [g for (inst, _), g in self._stats.items() if inst == installation_id]
        return sorted(stats, key=lambda g: g.request_count, reverse=True)[:limit]

    def total_countries(self, installation_id: str) -> int:
        return len([1 for (inst, _) in self._stats if inst == installation_id])

    def total_unique_ips(self, installation_id: str) -> int:
        all_ips: set[str] = set()
        for (inst, _), g in self._stats.items():
            if inst == installation_id: all_ips.update(g.unique_ips)
        return len(all_ips)

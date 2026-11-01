"""App Geo Routing — route requests based on geographic location.

Manages geographic routing for installed apps:
- Define regions with endpoints
- Resolve nearest region by country
- Track request distribution per region
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class GeoRegion:
    """A geographic routing region."""

    region_id: str
    name: str
    endpoint: str
    countries: list[str]  # ISO country codes
    request_count: int = 0
    active: bool = True


class AppGeoRouting:
    """Route requests based on geographic location."""

    def __init__(self, default_region: str = "") -> None:
        self._default = default_region
        self._regions: dict[tuple[str, str], GeoRegion] = {}

    def add_region(
        self,
        installation_id: str,
        region_id: str,
        name: str,
        endpoint: str,
        countries: list[str],
    ) -> GeoRegion:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not region_id:
            raise ValueError("region_id is required")
        if not endpoint:
            raise ValueError("endpoint is required")

        key = (installation_id, region_id)
        if key in self._regions:
            raise ValueError(f"Region {region_id} already exists")

        region = GeoRegion(
            region_id=region_id, name=name,
            endpoint=endpoint, countries=[c.upper() for c in countries],
        )
        self._regions[key] = region
        return region

    def resolve(self, installation_id: str, country_code: str) -> GeoRegion:
        """Resolve the region for a country code."""
        cc = country_code.upper()
        for (inst, _), region in self._regions.items():
            if inst == installation_id and region.active and cc in region.countries:
                region.request_count += 1
                return region

        # Fallback to default
        if self._default:
            key = (installation_id, self._default)
            default = self._regions.get(key)
            if default and default.active:
                default.request_count += 1
                return default

        raise KeyError(f"No region for country {cc}")

    def list_regions(self, installation_id: str) -> list[GeoRegion]:
        return [r for (inst, _), r in self._regions.items() if inst == installation_id]

    def disable_region(self, installation_id: str, region_id: str) -> GeoRegion:
        r = self._get(installation_id, region_id)
        r.active = False
        return r

    def _get(self, installation_id: str, region_id: str) -> GeoRegion:
        key = (installation_id, region_id)
        r = self._regions.get(key)
        if r is None:
            raise KeyError(f"Region {region_id} not found")
        return r

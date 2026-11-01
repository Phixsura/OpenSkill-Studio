"""API Consumer Request Geo Router — route requests to nearest regional backend."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class RegionalBackend:
    region: str
    endpoint: str
    healthy: bool = True
    latency_ms: float = 0.0
    load_pct: float = 0.0

@dataclass
class GeoRoutingConfig:
    default_region: str = "us-east"
    fallback_region: str = "eu-west"
    backends: list[RegionalBackend] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouter:
    def __init__(self) -> None:
        self._configs: dict[str, GeoRoutingConfig] = {}
        self._consumer_regions: dict[tuple[str, str], str] = {}

    def configure(self, installation_id: str, config: GeoRoutingConfig) -> GeoRoutingConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not config.backends: raise ValueError("At least one backend required")
        self._configs[installation_id] = config
        return config

    def set_consumer_region(self, installation_id: str, consumer_id: str, region: str) -> None:
        self._consumer_regions[(installation_id, consumer_id)] = region

    def route(self, installation_id: str, consumer_id: str) -> RegionalBackend | None:
        config = self._configs.get(installation_id)
        if config is None: return None
        healthy = [b for b in config.backends if b.healthy]
        if not healthy: return None
        # Consumer's preferred region
        preferred = self._consumer_regions.get((installation_id, consumer_id), config.default_region)
        match = next((b for b in healthy if b.region == preferred), None)
        if match: return match
        # Fallback
        fallback = next((b for b in healthy if b.region == config.fallback_region), None)
        if fallback: return fallback
        # Lowest load
        return min(healthy, key=lambda b: b.load_pct)

    def healthy_regions(self, installation_id: str) -> list[str]:
        config = self._configs.get(installation_id)
        if config is None: return []
        return list({b.region for b in config.backends if b.healthy})

"""API Endpoint Rate Limit Tier — per-endpoint rate limits based on consumer tier."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class TierLimit:
    tier: str  # "free", "starter", "pro", "enterprise"
    requests_per_minute: int
    requests_per_hour: int
    burst_size: int = 10

@dataclass
class EndpointTierConfig:
    endpoint: str
    method: str
    tiers: list[TierLimit] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointRateLimitTier:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], EndpointTierConfig] = {}

    def configure(self, installation_id: str, endpoint: str, method: str, tiers: list[TierLimit]) -> EndpointTierConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not tiers: raise ValueError("At least one tier required")
        for t in tiers:
            if t.requests_per_minute < 1: raise ValueError(f"Tier {t.tier}: rpm must be >= 1")
            if t.requests_per_hour < t.requests_per_minute: raise ValueError(f"Tier {t.tier}: rph must be >= rpm")
        key = (installation_id, method.upper(), endpoint)
        config = EndpointTierConfig(endpoint=endpoint, method=method.upper(), tiers=tiers)
        self._configs[key] = config
        return config

    def get_limit(self, installation_id: str, endpoint: str, method: str, consumer_tier: str) -> TierLimit | None:
        config = self._configs.get((installation_id, method.upper(), endpoint))
        if config is None: return None
        return next((t for t in config.tiers if t.tier == consumer_tier), None)

    def list_configs(self, installation_id: str) -> list[EndpointTierConfig]:
        return [c for (inst, _, _), c in self._configs.items() if inst == installation_id]

    def tiers_for_endpoint(self, installation_id: str, endpoint: str, method: str) -> list[TierLimit]:
        config = self._configs.get((installation_id, method.upper(), endpoint))
        return config.tiers if config else []

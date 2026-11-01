"""Request Geo Restriction — allow or block API requests by country."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GeoPolicy:
    policy_id: str
    mode: str = "allowlist"  # "allowlist" or "blocklist"
    countries: set[str] = field(default_factory=set)  # ISO 3166-1 alpha-2 codes

@dataclass
class GeoCheckResult:
    allowed: bool
    country: str
    reason: str  # "allowed_country", "blocked_country", "no_policy", "unknown_country"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], GeoPolicy] = {}  # (inst, consumer_id)
        self._stats: dict[tuple[str, str, str], int] = {}  # (inst, consumer, country) -> count

    def set_policy(self, installation_id: str, consumer_id: str, policy: GeoPolicy) -> GeoPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if policy.mode not in ("allowlist", "blocklist"):
            raise ValueError("mode must be 'allowlist' or 'blocklist'")
        # Normalize to uppercase
        policy.countries = {c.upper() for c in policy.countries}
        self._policies[(installation_id, consumer_id)] = policy
        log.info("geo_policy_set", installation_id=installation_id, consumer_id=consumer_id, mode=policy.mode, countries=len(policy.countries))
        return policy

    def check(self, installation_id: str, consumer_id: str, country_code: str) -> GeoCheckResult:
        cc = country_code.upper()
        policy = self._policies.get((installation_id, consumer_id))
        if not policy:
            return GeoCheckResult(allowed=True, country=cc, reason="no_policy")
        # Track stats
        self._stats[(installation_id, consumer_id, cc)] = self._stats.get((installation_id, consumer_id, cc), 0) + 1
        if policy.mode == "allowlist":
            if cc in policy.countries:
                return GeoCheckResult(allowed=True, country=cc, reason="allowed_country")
            return GeoCheckResult(allowed=False, country=cc, reason="blocked_country")
        else:  # blocklist
            if cc in policy.countries:
                return GeoCheckResult(allowed=False, country=cc, reason="blocked_country")
            return GeoCheckResult(allowed=True, country=cc, reason="allowed_country")

    def get_stats(self, installation_id: str, consumer_id: str) -> dict[str, int]:
        return {cc: count for (inst, cid, cc), count in self._stats.items() if inst == installation_id and cid == consumer_id}

    def get_policy(self, installation_id: str, consumer_id: str) -> GeoPolicy | None:
        return self._policies.get((installation_id, consumer_id))

"""API Consumer Geo Restriction — restrict API access by geographic region."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GeoPolicy:
    policy_id: str
    mode: str  # "allowlist" or "blocklist"
    regions: list[str] = field(default_factory=list)  # ISO country codes
    action: str = "block"  # "block" or "challenge"

VALID_MODES = {"allowlist", "blocklist"}
VALID_ACTIONS = {"block", "challenge", "log"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestriction:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], GeoPolicy] = {}

    def set_policy(self, installation_id: str, consumer_id: str, policy: GeoPolicy) -> GeoPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if policy.mode not in VALID_MODES: raise ValueError(f"Invalid mode: {policy.mode}")
        if policy.action not in VALID_ACTIONS: raise ValueError(f"Invalid action: {policy.action}")
        if not policy.regions: raise ValueError("At least one region required")
        for r in policy.regions:
            if len(r) != 2 or not r.isalpha(): raise ValueError(f"Invalid country code: {r}")
        self._policies[(installation_id, consumer_id)] = policy
        return policy

    def check_access(self, installation_id: str, consumer_id: str, country_code: str) -> dict[str, object]:
        policy = self._policies.get((installation_id, consumer_id))
        if policy is None: return {"allowed": True, "reason": "no_policy"}
        cc = country_code.upper()
        if policy.mode == "allowlist":
            allowed = cc in [r.upper() for r in policy.regions]
        else:  # blocklist
            allowed = cc not in [r.upper() for r in policy.regions]
        if not allowed:
            return {"allowed": False, "reason": f"geo_{policy.action}", "country": cc, "action": policy.action}
        return {"allowed": True, "country": cc}

    def list_policies(self, installation_id: str) -> list[tuple[str, GeoPolicy]]:
        return [(cid, p) for (inst, cid), p in self._policies.items() if inst == installation_id]

    def consumer_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._policies if inst == installation_id)

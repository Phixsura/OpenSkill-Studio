"""App API Developer API Endpoint Ownership — track which teams own which endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointOwnership:
    endpoint: str
    owner_team: str
    oncall_contact: str = ""
    sla_tier: str = "standard"  # "critical", "standard", "best_effort"
    last_updated_by: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnership:
    def __init__(self) -> None:
        self._ownership: dict[tuple[str, str], EndpointOwnership] = {}

    def assign(self, installation_id: str, endpoint: str, owner_team: str, oncall_contact: str = "", sla_tier: str = "standard") -> EndpointOwnership:
        if not installation_id: raise ValueError("installation_id is required")
        if sla_tier not in ("critical", "standard", "best_effort"): raise ValueError("invalid sla_tier")
        key = (installation_id, endpoint)
        o = EndpointOwnership(endpoint=endpoint, owner_team=owner_team, oncall_contact=oncall_contact, sla_tier=sla_tier)
        self._ownership[key] = o
        return o

    def by_team(self, installation_id: str, team: str) -> list[EndpointOwnership]:
        return [o for (inst, _), o in self._ownership.items() if inst == installation_id and o.owner_team == team]

    def unowned(self, installation_id: str, known_endpoints: list[str]) -> list[str]:
        owned = {ep for (inst, ep) in self._ownership if inst == installation_id}
        return [ep for ep in known_endpoints if ep not in owned]

    def team_distribution(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), o in self._ownership.items():
            if inst == installation_id: counts[o.owner_team] = counts.get(o.owner_team, 0) + 1
        return counts

    def all_ownership(self, installation_id: str) -> list[EndpointOwnership]:
        return [o for (inst, _), o in self._ownership.items() if inst == installation_id]

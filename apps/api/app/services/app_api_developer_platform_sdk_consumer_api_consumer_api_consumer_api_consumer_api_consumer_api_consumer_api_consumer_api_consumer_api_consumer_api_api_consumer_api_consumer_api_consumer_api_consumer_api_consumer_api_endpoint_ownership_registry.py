"""Consumer API Endpoint Ownership Registry — track who owns each endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class EndpointOwner:
    endpoint_path: str
    team: str
    owner_email: str
    on_call_email: str = ""
    sla_tier: str = "standard"
    created_at: datetime | None = None

@dataclass
class OwnershipReport:
    total_endpoints: int
    by_team: dict[str, int]
    unowned: list[str]

class AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry:
    def __init__(self) -> None:
        self._owners: dict[tuple[str, str], EndpointOwner] = {}

    def register(self, installation_id: str, owner: EndpointOwner) -> EndpointOwner:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not owner.team:
            raise ValueError("team is required")
        owner.created_at = owner.created_at or datetime.utcnow()
        self._owners[(installation_id, owner.endpoint_path)] = owner
        return owner

    def get_owner(self, installation_id: str, endpoint_path: str) -> EndpointOwner | None:
        return self._owners.get((installation_id, endpoint_path))

    def find_by_team(self, installation_id: str, team: str) -> list[EndpointOwner]:
        return sorted([o for (inst, _), o in self._owners.items() if inst == installation_id and o.team == team], key=lambda o: o.endpoint_path)

    def get_report(self, installation_id: str, all_endpoints: list[str] | None = None) -> OwnershipReport:
        owned = {ep for (inst, ep) in self._owners if inst == installation_id}
        by_team: dict[str, int] = {}
        for (inst, _), o in self._owners.items():
            if inst == installation_id:
                by_team[o.team] = by_team.get(o.team, 0) + 1
        unowned = sorted(set(all_endpoints or []) - owned)
        return OwnershipReport(total_endpoints=len(owned), by_team=by_team, unowned=unowned)

    def transfer(self, installation_id: str, endpoint_path: str, new_team: str, new_owner_email: str) -> EndpointOwner:
        key = (installation_id, endpoint_path)
        owner = self._owners.get(key)
        if not owner:
            raise ValueError("Endpoint not registered")
        owner.team = new_team
        owner.owner_email = new_owner_email
        return owner

    def list_all(self, installation_id: str) -> list[EndpointOwner]:
        return sorted([o for (inst, _), o in self._owners.items() if inst == installation_id], key=lambda o: o.endpoint_path)

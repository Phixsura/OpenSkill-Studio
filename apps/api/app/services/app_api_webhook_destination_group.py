"""App API Webhook Destination Group — group destinations for bulk operations."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DestinationGroup:
    group_id: str
    name: str
    destinations: list[str] = field(default_factory=list)
    enabled: bool = True

class AppAPIWebhookDestinationGroup:
    def __init__(self) -> None:
        self._groups: dict[tuple[str, str], DestinationGroup] = {}

    def create(self, installation_id: str, group_id: str, name: str, destinations: list[str]) -> DestinationGroup:
        if not installation_id: raise ValueError("installation_id is required")
        if not destinations: raise ValueError("at least one destination required")
        key = (installation_id, group_id)
        if key in self._groups: raise ValueError(f"Group {group_id} exists")
        g = DestinationGroup(group_id=group_id, name=name, destinations=list(destinations))
        self._groups[key] = g
        return g

    def add_destination(self, installation_id: str, group_id: str, destination: str) -> DestinationGroup:
        g = self._get(installation_id, group_id)
        if destination not in g.destinations: g.destinations.append(destination)
        return g

    def remove_destination(self, installation_id: str, group_id: str, destination: str) -> DestinationGroup:
        g = self._get(installation_id, group_id)
        if destination in g.destinations: g.destinations.remove(destination)
        return g

    def toggle(self, installation_id: str, group_id: str, enabled: bool) -> DestinationGroup:
        g = self._get(installation_id, group_id)
        g.enabled = enabled
        return g

    def active_groups(self, installation_id: str) -> list[DestinationGroup]:
        return [g for (inst, _), g in self._groups.items() if inst == installation_id and g.enabled]

    def list_groups(self, installation_id: str) -> list[DestinationGroup]:
        return [g for (inst, _), g in self._groups.items() if inst == installation_id]

    def _get(self, installation_id: str, group_id: str) -> DestinationGroup:
        g = self._groups.get((installation_id, group_id))
        if g is None: raise KeyError(f"Group {group_id} not found")
        return g

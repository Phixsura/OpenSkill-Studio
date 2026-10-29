"""App API Developer Webhook Priority Router — route webhooks by priority level."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

PRIORITIES = {"critical": 0, "high": 1, "normal": 2, "low": 3}

@dataclass
class PriorityRoute:
    route_id: str
    event_type: str
    priority: str
    destination: str
    delivered_count: int = 0

class AppAPIDeveloperAPIApiWebhookPriorityRouter:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], PriorityRoute] = {}

    def add_route(self, installation_id: str, route_id: str, event_type: str, priority: str, destination: str) -> PriorityRoute:
        if not installation_id: raise ValueError("installation_id is required")
        if priority not in PRIORITIES: raise ValueError(f"Invalid priority: {priority}")
        key = (installation_id, route_id)
        if key in self._routes: raise ValueError(f"Route {route_id} exists")
        r = PriorityRoute(route_id=route_id, event_type=event_type, priority=priority, destination=destination)
        self._routes[key] = r
        return r

    def resolve(self, installation_id: str, event_type: str) -> list[PriorityRoute]:
        routes = [r for (inst, _), r in self._routes.items() if inst == installation_id and r.event_type == event_type]
        return sorted(routes, key=lambda r: PRIORITIES.get(r.priority, 99))

    def deliver(self, installation_id: str, route_id: str) -> PriorityRoute:
        key = (installation_id, route_id)
        r = self._routes.get(key)
        if r is None: raise KeyError(f"Route {route_id} not found")
        r.delivered_count += 1
        return r

    def by_priority(self, installation_id: str, priority: str) -> list[PriorityRoute]:
        return [r for (inst, _), r in self._routes.items() if inst == installation_id and r.priority == priority]

    def all_routes(self, installation_id: str) -> list[PriorityRoute]:
        return [r for (inst, _), r in self._routes.items() if inst == installation_id]

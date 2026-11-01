"""App API Developer Webhook Destination Registry — register and manage webhook destinations."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WebhookDestination:
    destination_id: str
    url: str
    name: str
    active: bool = True
    registered_at: float = field(default_factory=time.time)
    total_deliveries: int = 0
    last_delivery_at: float = 0.0
    subscribed_events: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistry:
    def __init__(self) -> None:
        self._destinations: dict[tuple[str, str], WebhookDestination] = {}

    def register(self, installation_id: str, destination_id: str, url: str, name: str, subscribed_events: list[str] | None = None) -> WebhookDestination:
        if not installation_id: raise ValueError("installation_id is required")
        if not url.startswith("https://"): raise ValueError("URL must use HTTPS")
        key = (installation_id, destination_id)
        if key in self._destinations: raise ValueError(f"Destination {destination_id} exists")
        d = WebhookDestination(destination_id=destination_id, url=url, name=name, subscribed_events=subscribed_events or [])
        self._destinations[key] = d
        return d

    def deactivate(self, installation_id: str, destination_id: str) -> WebhookDestination:
        d = self._get(installation_id, destination_id)
        d.active = False
        return d

    def record_delivery(self, installation_id: str, destination_id: str) -> WebhookDestination:
        d = self._get(installation_id, destination_id)
        d.total_deliveries += 1
        d.last_delivery_at = time.time()
        return d

    def active_destinations(self, installation_id: str) -> list[WebhookDestination]:
        return [d for (inst, _), d in self._destinations.items() if inst == installation_id and d.active]

    def all_destinations(self, installation_id: str) -> list[WebhookDestination]:
        return [d for (inst, _), d in self._destinations.items() if inst == installation_id]

    def _get(self, installation_id: str, destination_id: str) -> WebhookDestination:
        key = (installation_id, destination_id)
        d = self._destinations.get(key)
        if d is None: raise KeyError(f"Destination {destination_id} not found")
        return d

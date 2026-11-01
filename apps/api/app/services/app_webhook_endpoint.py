"""App Webhook Endpoint — manage webhook endpoint registrations.

Manages webhook endpoints:
- Register endpoints with URL and event subscriptions
- Enable/disable endpoints
- Track delivery success per endpoint
- Per-installation scoped endpoints
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class WebhookEndpoint:
    """A webhook endpoint registration."""

    endpoint_id: str
    url: str
    events: list[str]  # subscribed event types
    enabled: bool = True
    description: str = ""
    success_count: int = 0
    failure_count: int = 0

    @property
    def total_deliveries(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        if self.total_deliveries == 0:
            return 100.0
        return round(self.success_count / self.total_deliveries * 100, 1)


class AppWebhookEndpoint:
    """Manage webhook endpoint registrations."""

    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], WebhookEndpoint] = {}

    def register(
        self, installation_id: str, endpoint_id: str, url: str,
        events: list[str], description: str = "",
    ) -> WebhookEndpoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not url:
            raise ValueError("url is required")
        if not events:
            raise ValueError("at least one event required")

        ep = WebhookEndpoint(
            endpoint_id=endpoint_id, url=url,
            events=events, description=description,
        )
        self._endpoints[(installation_id, endpoint_id)] = ep
        return ep

    def record_delivery(self, installation_id: str, endpoint_id: str, success: bool) -> WebhookEndpoint:
        ep = self._get(installation_id, endpoint_id)
        if success:
            ep.success_count += 1
        else:
            ep.failure_count += 1
        return ep

    def toggle(self, installation_id: str, endpoint_id: str, enabled: bool) -> WebhookEndpoint:
        ep = self._get(installation_id, endpoint_id)
        ep.enabled = enabled
        return ep

    def endpoints_for_event(self, installation_id: str, event_type: str) -> list[WebhookEndpoint]:
        return [
            ep for (inst, _), ep in self._endpoints.items()
            if inst == installation_id and ep.enabled and event_type in ep.events
        ]

    def list_endpoints(self, installation_id: str) -> list[WebhookEndpoint]:
        return [ep for (inst, _), ep in self._endpoints.items() if inst == installation_id]

    def _get(self, installation_id: str, endpoint_id: str) -> WebhookEndpoint:
        key = (installation_id, endpoint_id)
        ep = self._endpoints.get(key)
        if ep is None:
            raise KeyError(f"Endpoint {endpoint_id} not found")
        return ep

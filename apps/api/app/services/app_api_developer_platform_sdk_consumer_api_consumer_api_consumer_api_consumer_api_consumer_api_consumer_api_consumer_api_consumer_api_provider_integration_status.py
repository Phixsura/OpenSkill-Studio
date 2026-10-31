"""Consumer API Provider Integration Status — track third-party provider health."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ProviderStatus:
    provider_id: str
    name: str
    status: str = "operational"  # "operational", "degraded", "outage", "maintenance"
    latency_ms: float = 0.0
    last_checked_at: datetime | None = None
    error_message: str = ""

@dataclass
class IntegrationOverview:
    total_providers: int
    operational: int
    degraded: int
    outage: int
    overall_status: str

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus:
    def __init__(self) -> None:
        self._providers: dict[tuple[str, str], ProviderStatus] = {}

    def register(self, installation_id: str, provider: ProviderStatus) -> ProviderStatus:
        if not installation_id:
            raise ValueError("installation_id is required")
        if provider.status not in ("operational", "degraded", "outage", "maintenance"):
            raise ValueError(f"Invalid status: {provider.status}")
        self._providers[(installation_id, provider.provider_id)] = provider
        return provider

    def update_status(self, installation_id: str, provider_id: str, status: str, latency_ms: float = 0, error: str = "", now: datetime | None = None) -> ProviderStatus:
        key = (installation_id, provider_id)
        provider = self._providers.get(key)
        if not provider:
            raise ValueError("Provider not found")
        if status not in ("operational", "degraded", "outage", "maintenance"):
            raise ValueError(f"Invalid status: {status}")
        provider.status = status
        provider.latency_ms = latency_ms
        provider.error_message = error
        provider.last_checked_at = now or datetime.utcnow()
        return provider

    def get_overview(self, installation_id: str) -> IntegrationOverview:
        providers = [p for (inst, _), p in self._providers.items() if inst == installation_id]
        if not providers:
            return IntegrationOverview(total_providers=0, operational=0, degraded=0, outage=0, overall_status="operational")
        op = sum(1 for p in providers if p.status == "operational")
        deg = sum(1 for p in providers if p.status == "degraded")
        out = sum(1 for p in providers if p.status == "outage")
        if out > 0:
            overall = "outage"
        elif deg > 0:
            overall = "degraded"
        else:
            overall = "operational"
        return IntegrationOverview(total_providers=len(providers), operational=op, degraded=deg, outage=out, overall_status=overall)

    def list_providers(self, installation_id: str) -> list[ProviderStatus]:
        return sorted([p for (inst, _), p in self._providers.items() if inst == installation_id], key=lambda p: ({"outage": 0, "degraded": 1, "maintenance": 2, "operational": 3}.get(p.status, 4), p.name))

"""App API Developer Tenant Usage Report — per-tenant resource consumption."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class TenantUsage:
    tenant_id: str
    api_calls: int = 0
    webhook_deliveries: int = 0
    storage_bytes: int = 0
    compute_seconds: float = 0.0
    active_keys: int = 0

    @property
    def total_cost_cents(self) -> int:
        return int(self.api_calls * 0.001 + self.webhook_deliveries * 0.002 + self.storage_bytes / 1_073_741_824 * 10 + self.compute_seconds * 0.05)

class AppAPIDeveloperAPITenantUsageReport:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str], TenantUsage] = {}

    def record(self, installation_id: str, tenant_id: str, api_calls: int = 0, webhook_deliveries: int = 0, storage_bytes: int = 0, compute_seconds: float = 0.0, active_keys: int = 0) -> TenantUsage:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, tenant_id)
        if key not in self._usage:
            self._usage[key] = TenantUsage(tenant_id=tenant_id)
        u = self._usage[key]
        u.api_calls += api_calls
        u.webhook_deliveries += webhook_deliveries
        u.storage_bytes += storage_bytes
        u.compute_seconds += compute_seconds
        u.active_keys = active_keys
        return u

    def get(self, installation_id: str, tenant_id: str) -> TenantUsage | None:
        return self._usage.get((installation_id, tenant_id))

    def top_tenants(self, installation_id: str, by: str = "api_calls", limit: int = 10) -> list[TenantUsage]:
        tenants = [u for (inst, _), u in self._usage.items() if inst == installation_id]
        return sorted(tenants, key=lambda u: getattr(u, by, 0), reverse=True)[:limit]

    def total_cost_cents(self, installation_id: str) -> int:
        return sum(u.total_cost_cents for (inst, _), u in self._usage.items() if inst == installation_id)

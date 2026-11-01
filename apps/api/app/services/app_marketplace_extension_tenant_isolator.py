"""Multi-Tenant Isolator — data and resource isolation between tenants.

Implements:
- Tenant-scoped data access (automatic WHERE tenant_id = ?)
- Resource quotas per tenant
- Noisy neighbor detection
- Tenant-level feature flags
- Cross-tenant access prevention
- Tenant provisioning and deprovisioning
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import defaultdict


@dataclass
class TenantConfig:
    tenant_id: str
    name: str
    plan: str = "free"  # free, pro, enterprise
    active: bool = True
    created_at: float = 0.0
    quotas: dict[str, float] = field(default_factory=dict)
    features: dict[str, bool] = field(default_factory=dict)
    usage: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


PLAN_QUOTAS = {
    "free": {"api_calls": 1000, "storage_mb": 100, "users": 5},
    "pro": {"api_calls": 50000, "storage_mb": 5000, "users": 50},
    "enterprise": {"api_calls": 1000000, "storage_mb": 100000, "users": 1000},
}


class TenantIsolatorService:
    def __init__(self):
        self._tenants: dict[str, TenantConfig] = {}
        self._data_store: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

    def provision(self, tenant_id: str, name: str,
                  plan: str = "free") -> TenantConfig:
        if tenant_id in self._tenants:
            raise ValueError(f"Tenant {tenant_id} already exists")
        quotas = dict(PLAN_QUOTAS.get(plan, PLAN_QUOTAS["free"]))
        tenant = TenantConfig(tenant_id=tenant_id, name=name,
                              plan=plan, quotas=quotas)
        self._tenants[tenant_id] = tenant
        return tenant

    def deprovision(self, tenant_id: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        tenant.active = False
        # Clean up data
        self._data_store.pop(tenant_id, None)
        return True

    def check_access(self, tenant_id: str, requesting_tenant: str) -> bool:
        """Prevent cross-tenant access."""
        return tenant_id == requesting_tenant

    def store_data(self, tenant_id: str, collection: str,
                   data: dict) -> bool:
        """Store data scoped to tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant or not tenant.active:
            return False
        self._data_store[tenant_id][collection].append(data)
        tenant.usage["storage_items"] = tenant.usage.get("storage_items", 0) + 1
        return True

    def query_data(self, tenant_id: str, collection: str,
                   requesting_tenant: str) -> list[dict]:
        """Query data with tenant isolation enforcement."""
        if not self.check_access(tenant_id, requesting_tenant):
            raise PermissionError("Cross-tenant access denied")
        return list(self._data_store.get(tenant_id, {}).get(collection, []))

    def check_quota(self, tenant_id: str, resource: str,
                    amount: float = 1) -> dict:
        """Check if tenant has quota remaining."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return {"allowed": False, "reason": "tenant not found"}

        limit = tenant.quotas.get(resource, 0)
        used = tenant.usage.get(resource, 0)

        if used + amount > limit:
            return {"allowed": False, "used": used, "limit": limit,
                    "remaining": max(0, limit - used)}

        tenant.usage[resource] = used + amount
        return {"allowed": True, "used": used + amount, "limit": limit,
                "remaining": limit - used - amount}

    def set_feature(self, tenant_id: str, feature: str,
                    enabled: bool) -> bool:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        tenant.features[feature] = enabled
        return True

    def has_feature(self, tenant_id: str, feature: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        return tenant.features.get(feature, False) if tenant else False

    def detect_noisy_neighbors(self, resource: str,
                                threshold_pct: float = 50) -> list[str]:
        """Find tenants consuming > threshold% of total resource."""
        total = sum(t.usage.get(resource, 0) for t in self._tenants.values())
        if total == 0:
            return []
        return [t.tenant_id for t in self._tenants.values()
                if t.usage.get(resource, 0) / total * 100 > threshold_pct]

    def upgrade_plan(self, tenant_id: str, new_plan: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        if not tenant or new_plan not in PLAN_QUOTAS:
            return False
        tenant.plan = new_plan
        tenant.quotas.update(PLAN_QUOTAS[new_plan])
        return True

    def get_tenant_stats(self, tenant_id: str) -> dict:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return {}
        return {
            "tenant_id": tenant_id, "plan": tenant.plan,
            "active": tenant.active,
            "quotas": dict(tenant.quotas),
            "usage": dict(tenant.usage),
            "features": dict(tenant.features),
        }

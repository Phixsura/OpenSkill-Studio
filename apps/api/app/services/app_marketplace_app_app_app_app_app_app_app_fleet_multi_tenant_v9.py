"""Fleet Multi-Tenant v9 — track tenant isolation and resource usage."""
from __future__ import annotations
def fleet_multi_tenant_v9(tenants: list[dict]) -> dict:
    active = [t for t in tenants if t.get("active")]
    resource_usage = sum(t.get("resource_pct", 0) for t in tenants) / len(tenants) if tenants else 0
    noisy_neighbors = [t for t in tenants if t.get("resource_pct", 0) > 30]
    return {"tenants": len(tenants), "active": len(active), "avg_resource_pct": round(resource_usage, 1),
            "noisy_neighbors": len(noisy_neighbors), "healthy": len(noisy_neighbors) == 0}

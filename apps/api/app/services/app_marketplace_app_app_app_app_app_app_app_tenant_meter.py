"""Tenant usage metering — meter resource usage per tenant."""
from __future__ import annotations

_usage: dict[str, dict] = {}


def record_usage(tenant_id: str, resource: str, amount: float) -> dict:
    _usage.setdefault(tenant_id, {})
    _usage[tenant_id][resource] = _usage[tenant_id].get(resource, 0) + amount
    return {"tenant_id": tenant_id, "resource": resource,
            "total": round(_usage[tenant_id][resource], 2)}


def get_tenant_usage(tenant_id: str) -> dict:
    usage = _usage.get(tenant_id, {})
    return {"tenant_id": tenant_id, "resources": usage,
            "resource_count": len(usage),
            "total_units": round(sum(usage.values()), 2)}


def top_tenants(resource: str, limit: int = 10) -> list[dict]:
    results = []
    for tid, resources in _usage.items():
        if resource in resources:
            results.append({"tenant_id": tid, "usage": resources[resource]})
    return sorted(results, key=lambda r: -r["usage"])[:limit]


def clear_usage() -> None:
    _usage.clear()

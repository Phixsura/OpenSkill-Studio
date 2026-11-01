"""Multi-tenant isolation — enforce tenant boundaries."""
from __future__ import annotations


def validate_tenant_access(tenant_id: str, resource_tenant: str) -> dict:
    allowed = tenant_id == resource_tenant
    return {"allowed": allowed, "tenant": tenant_id, "resource_tenant": resource_tenant,
            "violation": not allowed}


def partition_data(records: list[dict], tenant_id: str) -> dict:
    own = [r for r in records if r.get("tenant_id") == tenant_id]
    leaked = [r for r in records if r.get("tenant_id") != tenant_id]
    return {"own_records": own, "own_count": len(own),
            "total": len(records), "leaked_count": len(leaked),
            "isolation_intact": len(leaked) == 0 or len(own) == len(records)}


def tenant_stats(tenants: dict[str, dict]) -> dict:
    total = len(tenants)
    active = sum(1 for t in tenants.values() if t.get("status") == "active")
    total_users = sum(t.get("user_count", 0) for t in tenants.values())
    total_storage = sum(t.get("storage_mb", 0) for t in tenants.values())
    return {"total_tenants": total, "active": active, "suspended": total - active,
            "total_users": total_users, "total_storage_mb": round(total_storage, 1)}

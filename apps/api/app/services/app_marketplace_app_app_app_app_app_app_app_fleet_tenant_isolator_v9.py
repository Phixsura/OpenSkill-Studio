"""Fleet Tenant Isolator v9 — track multi-tenant resource isolation."""
from __future__ import annotations
def fleet_tenant_isolator_v9(tenants: list[dict]) -> dict:
    isolated = [t for t in tenants if t.get("isolated", True)]
    violations = sum(t.get("violations", 0) for t in tenants)
    namespaces = sum(t.get("namespaces", 0) for t in tenants)
    return {"tenants": len(tenants), "isolated": len(isolated), "violations": violations,
            "total_namespaces": namespaces, "healthy": violations == 0}

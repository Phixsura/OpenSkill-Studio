"""Fleet API Tenant Isolation v9 — track multi-tenant API isolation."""
from __future__ import annotations
def fleet_api_tenant_isolation_v9(tenants: list[dict]) -> dict:
    isolated = [t for t in tenants if t.get("isolated")]
    violations = sum(t.get("violations", 0) for t in tenants)
    data_leaks = sum(t.get("data_leaks", 0) for t in tenants)
    return {"tenants": len(tenants), "isolated": len(isolated), "violations": violations,
            "data_leaks": data_leaks, "healthy": violations == 0 and data_leaks == 0}

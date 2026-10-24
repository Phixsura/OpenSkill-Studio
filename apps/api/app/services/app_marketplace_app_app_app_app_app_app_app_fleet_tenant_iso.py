"""Fleet tenant isolation — track isolation enforcement."""
from __future__ import annotations
def fleet_tenant_isolation(tenants: list[dict]) -> dict:
    isolated = [t for t in tenants if t.get("namespace_isolated", False)]
    shared = len(tenants) - len(isolated)
    return {"total": len(tenants), "isolated": len(isolated), "shared": shared,
            "fully_isolated": shared == 0}

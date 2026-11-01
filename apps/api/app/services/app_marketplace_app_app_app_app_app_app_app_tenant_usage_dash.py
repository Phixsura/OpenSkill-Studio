"""Tenant usage dashboard — unified tenant usage view."""
from __future__ import annotations


def tenant_dashboard(tenant: dict) -> dict:
    api_usage = tenant.get("api_calls", 0)
    api_limit = tenant.get("api_limit", 10000)
    storage_gb = tenant.get("storage_gb", 0)
    storage_limit = tenant.get("storage_limit_gb", 100)
    bandwidth_gb = tenant.get("bandwidth_gb", 0)
    bandwidth_limit = tenant.get("bandwidth_limit_gb", 500)
    usage = {
        "api_calls": {"used": api_usage, "limit": api_limit,
                       "pct": round(api_usage / max(api_limit, 1) * 100, 1)},
        "storage": {"used": storage_gb, "limit": storage_limit,
                     "pct": round(storage_gb / max(storage_limit, 1) * 100, 1)},
        "bandwidth": {"used": bandwidth_gb, "limit": bandwidth_limit,
                       "pct": round(bandwidth_gb / max(bandwidth_limit, 1) * 100, 1)},
    }
    any_exceeded = any(u["pct"] >= 100 for u in usage.values())
    any_warning = any(80 <= u["pct"] < 100 for u in usage.values())
    status = "exceeded" if any_exceeded else ("warning" if any_warning else "ok")
    return {"tenant_id": tenant.get("id", ""), "plan": tenant.get("plan", "free"),
            "usage": usage, "status": status}

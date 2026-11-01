"""Fleet Mesh Observability v9 — track service mesh telemetry collection."""
from __future__ import annotations
def fleet_mesh_observ_v9(proxies: list[dict]) -> dict:
    active = [p for p in proxies if p.get("active", True)]
    rps = sum(p.get("rps", 0) for p in proxies)
    error_rate = sum(p.get("error_rate", 0) for p in proxies) / len(proxies) if proxies else 0
    return {"proxies": len(proxies), "active": len(active), "total_rps": rps,
            "avg_error_rate": round(error_rate, 3), "healthy": error_rate < 1}

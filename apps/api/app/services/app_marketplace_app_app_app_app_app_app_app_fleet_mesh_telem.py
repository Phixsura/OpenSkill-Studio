"""Fleet mesh telemetry — aggregate service mesh metrics."""
from __future__ import annotations
def fleet_mesh_telemetry(proxies: list[dict]) -> dict:
    total_rps = sum(p.get("rps", 0) for p in proxies)
    avg_lat = round(sum(p.get("latency_ms", 0) for p in proxies) / max(len(proxies), 1), 1)
    errors = sum(p.get("error_count", 0) for p in proxies)
    return {"proxies": len(proxies), "total_rps": total_rps, "avg_latency_ms": avg_lat,
            "errors": errors, "healthy": errors == 0}

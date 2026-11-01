"""Gateway upstream health — monitor health of upstream backends."""
from __future__ import annotations


def check_upstreams(upstreams: list[dict]) -> dict:
    healthy = []
    unhealthy = []
    for u in upstreams:
        success_rate = round((u.get("successes", 0) / max(u.get("total", 1), 1)) * 100, 1)
        avg_ms = round(u.get("total_ms", 0) / max(u.get("total", 1), 1), 1)
        is_healthy = success_rate >= 95 and avg_ms < u.get("timeout_ms", 5000)
        entry = {"name": u["name"], "address": u.get("address", ""),
                 "success_rate": success_rate, "avg_ms": avg_ms, "healthy": is_healthy}
        if is_healthy:
            healthy.append(entry)
        else:
            unhealthy.append(entry)
    return {"healthy": len(healthy), "unhealthy": len(unhealthy),
            "total": len(upstreams), "all_healthy": len(unhealthy) == 0,
            "upstreams": healthy + unhealthy}

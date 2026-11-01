"""API gateway health — monitor gateway health across regions."""
from __future__ import annotations


def gateway_health(gateways: list[dict]) -> dict:
    healthy = [g for g in gateways if g.get("status") == "healthy"]
    by_region: dict[str, dict] = {}
    for g in gateways:
        region = g.get("region", "default")
        if region not in by_region:
            by_region[region] = {"healthy": 0, "total": 0}
        by_region[region]["total"] += 1
        if g["status"] == "healthy":
            by_region[region]["healthy"] += 1
    return {"total": len(gateways), "healthy": len(healthy),
            "all_healthy": len(healthy) == len(gateways),
            "by_region": by_region,
            "avg_latency_ms": round(sum(g.get("latency_ms", 0) for g in gateways) / max(len(gateways), 1), 1)}

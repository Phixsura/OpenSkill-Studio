"""DNS monitoring — monitor DNS resolution health and latency."""
from __future__ import annotations


def monitor_dns(domains: list[dict]) -> dict:
    results = []
    healthy = 0
    for d in domains:
        latency = d.get("resolve_ms", 0)
        resolved = d.get("resolved", True)
        ok = resolved and latency < d.get("threshold_ms", 100)
        if ok:
            healthy += 1
        results.append({"domain": d["domain"], "resolved": resolved,
                         "latency_ms": latency, "healthy": ok})
    total = len(results)
    return {"results": results, "total": total, "healthy": healthy,
            "unhealthy": total - healthy,
            "all_healthy": healthy == total}

"""Endpoint health checker — monitor individual API endpoint health and latency."""
from __future__ import annotations


def check_endpoints(endpoints: list[dict]) -> dict:
    results = []
    healthy = 0
    total_latency = 0
    for ep in endpoints:
        status = ep.get("status_code", 200)
        latency = ep.get("latency_ms", 0)
        ok = 200 <= status < 400 and latency < ep.get("max_latency_ms", 5000)
        if ok:
            healthy += 1
        total_latency += latency
        results.append({
            "path": ep["path"], "method": ep.get("method", "GET"),
            "status_code": status, "latency_ms": latency,
            "healthy": ok, "response_size_bytes": ep.get("response_size", 0),
        })
    total = len(endpoints)
    avg_latency = round(total_latency / max(total, 1), 1)
    return {
        "total": total, "healthy": healthy, "unhealthy": total - healthy,
        "health_pct": round(healthy / max(total, 1) * 100),
        "avg_latency_ms": avg_latency,
        "overall": "healthy" if healthy == total else "degraded" if healthy > 0 else "down",
        "results": sorted(results, key=lambda r: -r["latency_ms"]),
    }

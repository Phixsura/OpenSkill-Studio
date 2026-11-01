"""API status widget — compact status indicator for dashboards."""
from __future__ import annotations


def build_api_status(endpoints: list[dict]) -> dict:
    total = len(endpoints)
    healthy = sum(1 for e in endpoints if e.get("healthy", True))
    avg_latency = round(sum(e.get("latency_ms", 0) for e in endpoints) / max(total, 1), 1)
    status = "operational" if healthy == total else "degraded" if healthy > 0 else "outage"
    icon = "🟢" if status == "operational" else "🟡" if status == "degraded" else "🔴"
    return {
        "status": status, "icon": icon,
        "healthy": healthy, "total": total,
        "health_display": f"{healthy}/{total}",
        "avg_latency_ms": avg_latency,
        "latency_display": f"{avg_latency}ms",
    }

"""Marketplace health report — overall platform health snapshot."""


def build_marketplace_health(*, total_apps: int, healthy_pct: float, avg_latency_ms: float,
                               webhook_success_pct: float, active_developers: int) -> dict:
    status = "healthy" if healthy_pct >= 95 and webhook_success_pct >= 98 else \
             "degraded" if healthy_pct >= 80 else "critical"
    return {
        "status": status,
        "total_apps": total_apps,
        "healthy_pct": round(healthy_pct, 1),
        "avg_latency_ms": round(avg_latency_ms, 1),
        "webhook_success_pct": round(webhook_success_pct, 1),
        "active_developers": active_developers,
        "grade": "A" if status == "healthy" else "B" if status == "degraded" else "C",
    }

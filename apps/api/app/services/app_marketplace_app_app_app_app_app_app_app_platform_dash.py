"""Platform dashboard aggregator — aggregate all platform metrics."""
from __future__ import annotations


def build_dashboard(metrics: dict) -> dict:
    apps = metrics.get("apps", {})
    infra = metrics.get("infra", {})
    users = metrics.get("users", {})
    health_score = round(
        (apps.get("healthy_pct", 100) * 0.4 +
         infra.get("uptime_pct", 100) * 0.4 +
         users.get("satisfaction_pct", 100) * 0.2), 1)
    status = "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "critical"
    return {
        "health_score": health_score, "status": status,
        "apps": {"total": apps.get("total", 0), "active": apps.get("active", 0),
                 "healthy_pct": apps.get("healthy_pct", 100)},
        "infra": {"services": infra.get("services", 0), "uptime_pct": infra.get("uptime_pct", 100),
                  "incidents": infra.get("incidents", 0)},
        "users": {"total": users.get("total", 0), "active_today": users.get("active_today", 0),
                  "satisfaction_pct": users.get("satisfaction_pct", 100)},
    }


def trend_indicator(current: float, previous: float) -> dict:
    delta = round(current - previous, 2)
    pct = round(delta / max(abs(previous), 0.01) * 100, 1)
    return {"current": current, "previous": previous, "delta": delta,
            "pct_change": pct, "trend": "up" if delta > 0 else "down" if delta < 0 else "flat"}

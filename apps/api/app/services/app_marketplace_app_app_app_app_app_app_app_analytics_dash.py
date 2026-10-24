"""Platform analytics dashboard — aggregate platform-wide analytics."""
from __future__ import annotations


def build_analytics(data: dict) -> dict:
    active_apps = data.get("active_apps", 0)
    total_requests = data.get("total_requests", 0)
    avg_latency = data.get("avg_latency_ms", 0)
    error_rate = data.get("error_rate_pct", 0)
    dau = data.get("daily_active_users", 0)
    revenue = data.get("monthly_revenue", 0)
    health = "excellent" if error_rate < 1 and avg_latency < 100 else "good" if error_rate < 5 else "needs_improvement"
    return {"active_apps": active_apps, "total_requests": total_requests,
            "avg_latency_ms": avg_latency, "error_rate_pct": error_rate,
            "daily_active_users": dau, "monthly_revenue": revenue,
            "health": health, "display_revenue": f"${revenue:,.0f}",
            "display_requests": f"{total_requests / 1_000_000:.1f}M" if total_requests >= 1_000_000 else f"{total_requests:,}"}

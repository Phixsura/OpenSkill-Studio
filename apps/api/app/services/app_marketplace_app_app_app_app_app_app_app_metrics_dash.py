"""Platform metrics dashboard — aggregate key metrics for executive view."""
from __future__ import annotations


def executive_dashboard(metrics: dict) -> dict:
    uptime = metrics.get("uptime_pct", 99.99)
    error_rate = metrics.get("error_rate_pct", 0.01)
    p99 = metrics.get("p99_ms", 100)
    daily_users = metrics.get("daily_active_users", 0)
    api_calls = metrics.get("daily_api_calls", 0)
    health = "green" if uptime >= 99.9 and error_rate < 1 else (
        "yellow" if uptime >= 99 else "red")
    return {"health": health, "uptime_pct": uptime, "error_rate_pct": error_rate,
            "p99_latency_ms": p99, "daily_active_users": daily_users,
            "daily_api_calls": api_calls,
            "sla_met": uptime >= metrics.get("sla_target", 99.9)}


def trend_analysis(current: dict, previous: dict) -> dict:
    trends = {}
    for key in current:
        if key in previous and isinstance(current[key], (int, float)):
            delta = current[key] - previous[key]
            pct = round(delta / max(abs(previous[key]), 0.01) * 100, 1)
            direction = "up" if delta > 0 else ("down" if delta < 0 else "flat")
            trends[key] = {"current": current[key], "previous": previous[key],
                           "delta": round(delta, 2), "pct_change": pct, "direction": direction}
    return trends

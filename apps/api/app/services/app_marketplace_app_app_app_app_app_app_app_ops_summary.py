"""Platform ops summary — executive operations summary."""
from __future__ import annotations


def generate_ops_summary(metrics: dict) -> dict:
    uptime = metrics.get("uptime_pct", 99.9)
    deploys = metrics.get("deploys_today", 0)
    incidents = metrics.get("open_incidents", 0)
    error_rate = metrics.get("error_rate", 0)
    change_count = metrics.get("changes_24h", 0)
    risk = "low" if incidents == 0 and error_rate < 1 else "medium" if incidents <= 2 else "high"
    return {"uptime_pct": uptime, "deploys_today": deploys,
            "open_incidents": incidents, "error_rate": error_rate,
            "changes_24h": change_count, "risk_level": risk,
            "status": "nominal" if risk == "low" else "elevated" if risk == "medium" else "critical"}

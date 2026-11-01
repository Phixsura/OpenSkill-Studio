"""Resource monitor — track resource utilization across the platform."""
from __future__ import annotations


def monitor_resources(resources: list[dict]) -> dict:
    critical = []
    warnings = []
    healthy = 0
    for r in resources:
        usage_pct = r.get("usage_pct", 0)
        if usage_pct >= 90:
            critical.append({"name": r["name"], "type": r.get("type", ""), "usage_pct": usage_pct})
        elif usage_pct >= 70:
            warnings.append({"name": r["name"], "type": r.get("type", ""), "usage_pct": usage_pct})
        else:
            healthy += 1
    total_usage = round(sum(r.get("usage_pct", 0) for r in resources) / max(len(resources), 1), 1)
    return {"total": len(resources), "healthy": healthy,
            "warnings": warnings, "warning_count": len(warnings),
            "critical": critical, "critical_count": len(critical),
            "avg_usage_pct": total_usage,
            "status": "critical" if critical else "warning" if warnings else "healthy"}


def resource_trend(history: list[float]) -> dict:
    if len(history) < 2:
        return {"trend": "unknown"}
    recent = history[-3:] if len(history) >= 3 else history
    avg_recent = sum(recent) / len(recent)
    avg_old = sum(history[:-len(recent)]) / max(len(history) - len(recent), 1)
    delta = round(avg_recent - avg_old, 1)
    return {"trend": "increasing" if delta > 5 else "decreasing" if delta < -5 else "stable",
            "delta": delta, "current_avg": round(avg_recent, 1)}

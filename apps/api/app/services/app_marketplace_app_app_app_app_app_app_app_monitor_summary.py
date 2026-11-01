"""API monitoring summary — aggregate all monitoring signals into one view."""
from __future__ import annotations


def monitoring_summary(data: dict) -> dict:
    uptime = data.get("uptime_pct", 100)
    error_rate = data.get("error_rate_pct", 0)
    p99 = data.get("p99_ms", 0)
    rps = data.get("rps", 0)
    cpu = data.get("cpu_pct", 0)
    memory = data.get("memory_pct", 0)
    alerts = data.get("active_alerts", 0)
    incidents = data.get("open_incidents", 0)

    score = 100
    if uptime < 99.9: score -= 20
    if error_rate > 1: score -= 15
    if p99 > 500: score -= 10
    if cpu > 80: score -= 10
    if memory > 80: score -= 10
    if alerts > 0: score -= 5 * min(alerts, 5)
    if incidents > 0: score -= 10 * min(incidents, 3)
    score = max(0, score)

    status = "healthy" if score >= 80 else ("degraded" if score >= 50 else "critical")
    return {"score": score, "status": status, "uptime_pct": uptime,
            "error_rate_pct": error_rate, "p99_ms": p99, "rps": rps,
            "cpu_pct": cpu, "memory_pct": memory,
            "active_alerts": alerts, "open_incidents": incidents}

"""Gateway health summary — unified gateway health from all signals."""
from __future__ import annotations


def gateway_health_summary(metrics: dict) -> dict:
    rps = metrics.get("rps", 0)
    error_rate = metrics.get("error_rate_pct", 0)
    p99 = metrics.get("p99_ms", 0)
    uptime = metrics.get("uptime_pct", 100)
    active_conns = metrics.get("active_connections", 0)
    max_conns = metrics.get("max_connections", 10000)
    conn_util = round(active_conns / max(max_conns, 1) * 100, 1)
    score = 100
    if uptime < 99.9: score -= 20
    if error_rate > 1: score -= 15
    if p99 > 500: score -= 10
    if conn_util > 80: score -= 10
    score = max(0, score)
    status = "healthy" if score >= 80 else ("degraded" if score >= 50 else "critical")
    return {"score": score, "status": status, "rps": rps, "error_rate_pct": error_rate,
            "p99_ms": p99, "uptime_pct": uptime, "conn_util_pct": conn_util}

"""System metrics collector — collect CPU, memory, disk metrics."""
from __future__ import annotations


def collect_metrics(cpu_pct: float, memory_pct: float, disk_pct: float,
                     network_mbps: float = 0) -> dict:
    status = "healthy"
    alerts = []
    if cpu_pct > 90:
        alerts.append({"metric": "cpu", "value": cpu_pct, "threshold": 90})
        status = "critical"
    elif cpu_pct > 70:
        alerts.append({"metric": "cpu", "value": cpu_pct, "threshold": 70})
        status = "warning"
    if memory_pct > 90:
        alerts.append({"metric": "memory", "value": memory_pct, "threshold": 90})
        status = "critical"
    if disk_pct > 85:
        alerts.append({"metric": "disk", "value": disk_pct, "threshold": 85})
        if status != "critical":
            status = "warning"
    return {"cpu_pct": cpu_pct, "memory_pct": memory_pct, "disk_pct": disk_pct,
            "network_mbps": network_mbps, "status": status,
            "alerts": alerts, "alert_count": len(alerts)}


def trend_metrics(history: list[dict]) -> dict:
    if len(history) < 2:
        return {"trend": "insufficient_data"}
    latest = history[-1]
    previous = history[-2]
    cpu_delta = round(latest["cpu_pct"] - previous["cpu_pct"], 1)
    mem_delta = round(latest["memory_pct"] - previous["memory_pct"], 1)
    return {"cpu_trend": "up" if cpu_delta > 0 else "down" if cpu_delta < 0 else "stable",
            "mem_trend": "up" if mem_delta > 0 else "down" if mem_delta < 0 else "stable",
            "cpu_delta": cpu_delta, "mem_delta": mem_delta}

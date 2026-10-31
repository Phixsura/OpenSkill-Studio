"""Service capacity alert — alert when services approach capacity limits."""
from __future__ import annotations


def check_capacity_alerts(services: list[dict]) -> dict:
    alerts = []
    for s in services:
        cpu = s.get("cpu_pct", 0)
        mem = s.get("memory_pct", 0)
        conn = s.get("conn_pct", 0)
        max_util = max(cpu, mem, conn)
        if max_util >= 90:
            severity = "critical"
        elif max_util >= 75:
            severity = "warning"
        else:
            continue
        bottleneck = "cpu" if cpu == max_util else ("memory" if mem == max_util else "connections")
        alerts.append({"service": s["name"], "severity": severity,
                        "bottleneck": bottleneck, "utilization": max_util})
    alerts.sort(key=lambda a: -a["utilization"])
    return {"alerts": alerts, "total_alerts": len(alerts),
            "critical": sum(1 for a in alerts if a["severity"] == "critical"),
            "services_checked": len(services)}

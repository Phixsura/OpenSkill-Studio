"""Sandbox resource monitor — track CPU, memory, and network usage of sandboxed apps."""


def get_resource_snapshot(*, app_id: str, sandbox_id: str) -> dict:
    return {
        "app_id": app_id,
        "sandbox_id": sandbox_id,
        "cpu": {"usage_pct": 42.5, "limit_cores": 2, "used_cores": 0.85},
        "memory": {"usage_mb": 256, "limit_mb": 512, "usage_pct": 50.0},
        "disk": {"usage_mb": 120, "limit_mb": 1024, "usage_pct": 11.7},
        "network": {"rx_kb": 4500, "tx_kb": 1200, "connections": 8, "limit_connections": 50},
        "status": "running",
        "uptime_sec": 3600,
    }


def check_resource_limits(*, snapshot: dict) -> dict:
    alerts = []
    if snapshot["cpu"]["usage_pct"] > 80:
        alerts.append({"resource": "cpu", "severity": "warning", "value": snapshot["cpu"]["usage_pct"]})
    if snapshot["memory"]["usage_pct"] > 90:
        alerts.append({"resource": "memory", "severity": "critical", "value": snapshot["memory"]["usage_pct"]})
    if snapshot["disk"]["usage_pct"] > 80:
        alerts.append({"resource": "disk", "severity": "warning", "value": snapshot["disk"]["usage_pct"]})
    if snapshot["network"]["connections"] > snapshot["network"]["limit_connections"] * 0.8:
        alerts.append({"resource": "network", "severity": "warning", "value": snapshot["network"]["connections"]})
    return {"alerts": alerts, "alert_count": len(alerts),
            "healthy": len(alerts) == 0}

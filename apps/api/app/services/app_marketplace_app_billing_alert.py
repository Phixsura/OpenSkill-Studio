"""Billing alert — set thresholds and notify on spending anomalies."""


def create_alert(*, app_id: str, alert_type: str, threshold: float,
                   notify_channels: list[str]) -> dict:
    valid_types = {"monthly_spend", "daily_spend", "api_calls", "overage"}
    if alert_type not in valid_types:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(valid_types))}"}
    if threshold <= 0:
        return {"error": "Threshold must be positive"}
    return {
        "alert_id": f"alert_{abs(hash(f'{app_id}:{alert_type}')) % 100000:05d}",
        "app_id": app_id,
        "type": alert_type,
        "threshold": threshold,
        "notify_channels": notify_channels,
        "status": "active",
    }


def evaluate_alerts(*, alerts: list[dict], current_values: dict) -> dict:
    triggered = []
    for alert in alerts:
        current = current_values.get(alert["type"], 0)
        if current >= alert["threshold"]:
            pct = round(current / alert["threshold"] * 100, 1)
            triggered.append({
                "alert_id": alert["alert_id"],
                "type": alert["type"],
                "threshold": alert["threshold"],
                "current": current,
                "exceeded_by_pct": round(pct - 100, 1),
                "severity": "critical" if pct > 150 else "warning",
            })
    return {"triggered": triggered, "triggered_count": len(triggered),
            "total_alerts": len(alerts), "all_clear": len(triggered) == 0}

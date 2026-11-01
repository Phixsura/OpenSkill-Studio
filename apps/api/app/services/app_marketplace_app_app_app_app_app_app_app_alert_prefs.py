"""Alert preference manager — configure alert thresholds and notification channels."""
from __future__ import annotations

DEFAULT_ALERTS = {
    "error_rate": {"threshold": 5.0, "unit": "%", "channel": "email", "enabled": True},
    "latency_p99": {"threshold": 1000, "unit": "ms", "channel": "slack", "enabled": True},
    "uptime": {"threshold": 99.5, "unit": "%", "channel": "pagerduty", "enabled": True},
    "disk_usage": {"threshold": 90, "unit": "%", "channel": "email", "enabled": True},
    "cpu_usage": {"threshold": 85, "unit": "%", "channel": "slack", "enabled": False},
}


def get_alert_prefs() -> list[dict]:
    return [{"metric": k, **v} for k, v in DEFAULT_ALERTS.items()]


def update_alert(metric: str, *, threshold: float | None = None,
                   channel: str | None = None, enabled: bool | None = None) -> dict:
    alert = DEFAULT_ALERTS.get(metric)
    if not alert:
        return {"error": f"Unknown metric: {metric}"}
    if threshold is not None:
        alert["threshold"] = threshold
    if channel is not None:
        alert["channel"] = channel
    if enabled is not None:
        alert["enabled"] = enabled
    return {"metric": metric, **alert}


def check_alert(metric: str, value: float) -> dict:
    alert = DEFAULT_ALERTS.get(metric)
    if not alert or not alert["enabled"]:
        return {"triggered": False, "reason": "disabled"}
    if metric in ("uptime",):
        triggered = value < alert["threshold"]
    else:
        triggered = value > alert["threshold"]
    return {"triggered": triggered, "metric": metric, "value": value,
            "threshold": alert["threshold"], "channel": alert["channel"]}

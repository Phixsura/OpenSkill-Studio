"""Error budget burn alert — alert when error budget burns too fast."""
from __future__ import annotations


def check_burn_alert(burn_rate: float, windows: list[dict]) -> dict:
    alerts = []
    for w in windows:
        window_burn = w.get("burn_rate", 0)
        threshold = w.get("threshold", 1)
        if window_burn > threshold:
            severity = "critical" if window_burn > threshold * 10 else ("warning" if window_burn > threshold * 2 else "info")
            alerts.append({"window": w["name"], "burn_rate": window_burn,
                           "threshold": threshold, "severity": severity})
    firing = len(alerts) > 0
    most_severe = max((a["severity"] for a in alerts), key=lambda s: {"critical": 2, "warning": 1, "info": 0}.get(s, 0), default="none") if alerts else "none"
    return {"firing": firing, "alerts": alerts, "current_burn_rate": burn_rate,
            "most_severe": most_severe}


def should_page(alert: dict) -> dict:
    page = alert.get("most_severe") == "critical"
    return {"page": page, "channel": "pagerduty" if page else "slack",
            "severity": alert.get("most_severe", "none")}

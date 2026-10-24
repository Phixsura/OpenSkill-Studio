"""Anomaly alert manager — manage anomaly-based alerts with suppression."""
from __future__ import annotations
import time


class AnomalyAlertManager:
    def __init__(self, suppression_seconds: int = 300):
        self._alerts: list[dict] = []
        self._suppressed: dict[str, float] = {}
        self._suppression = suppression_seconds

    def fire(self, alert_name: str, metric: str, value: float, threshold: float,
             severity: str = "warning") -> dict:
        now = time.time()
        if alert_name in self._suppressed and now - self._suppressed[alert_name] < self._suppression:
            return {"fired": False, "reason": "suppressed"}
        alert = {"name": alert_name, "metric": metric, "value": value,
                 "threshold": threshold, "severity": severity, "fired_at": now}
        self._alerts.append(alert)
        self._suppressed[alert_name] = now
        return {"fired": True, "alert": alert}

    def acknowledge(self, alert_name: str) -> dict:
        for a in reversed(self._alerts):
            if a["name"] == alert_name:
                a["acknowledged"] = True
                return {"acknowledged": True}
        return {"acknowledged": False}

    def active_alerts(self) -> list[dict]:
        return [a for a in self._alerts if not a.get("acknowledged")]

    def stats(self) -> dict:
        return {"total_fired": len(self._alerts),
                "active": len(self.active_alerts()),
                "suppressed_keys": len(self._suppressed)}

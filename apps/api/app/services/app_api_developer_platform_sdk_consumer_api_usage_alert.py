"""Consumer API Usage Alert — usage threshold alerting with escalation."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

ALERT_LEVELS = ("info", "warning", "critical")
ESCALATION_CHANNELS = ("email", "slack", "pagerduty", "webhook")


@dataclass
class AlertThreshold:
    threshold_id: str
    metric_name: str
    operator: str  # gt, lt, gte, lte
    value: float
    alert_level: str = "warning"
    escalation_channel: str = "email"
    cooldown_seconds: float = 300.0
    enabled: bool = True


@dataclass
class FiredAlert:
    threshold_id: str
    metric_name: str
    actual_value: float
    threshold_value: float
    alert_level: str
    channel: str
    fired_at: float = 0.0


@dataclass
class UsageAlertManager:
    """Monitor usage metrics and fire alerts when thresholds are exceeded."""

    _thresholds: dict[str, AlertThreshold] = field(default_factory=dict)
    _fired: list[FiredAlert] = field(default_factory=list)
    _last_fired: dict[str, float] = field(default_factory=dict)  # threshold_id -> last fire time

    def add_threshold(self, threshold: AlertThreshold) -> dict:
        if threshold.threshold_id in self._thresholds:
            raise ValueError(f"Threshold {threshold.threshold_id} already exists")
        if threshold.alert_level not in ALERT_LEVELS:
            raise ValueError(f"Invalid alert level: {threshold.alert_level}")
        if threshold.operator not in ("gt", "lt", "gte", "lte"):
            raise ValueError(f"Invalid operator: {threshold.operator}")
        self._thresholds[threshold.threshold_id] = threshold
        logger.info("alert_threshold_added", threshold_id=threshold.threshold_id)
        return {"threshold_id": threshold.threshold_id, "metric": threshold.metric_name}

    def evaluate(self, metric_name: str, value: float, current_time: float = 0.0) -> list[dict]:
        alerts_fired = []
        for t in self._thresholds.values():
            if t.metric_name != metric_name or not t.enabled:
                continue
            triggered = False
            if t.operator == "gt" and value > t.value:
                triggered = True
            elif t.operator == "lt" and value < t.value:
                triggered = True
            elif t.operator == "gte" and value >= t.value:
                triggered = True
            elif t.operator == "lte" and value <= t.value:
                triggered = True
            if triggered:
                last = self._last_fired.get(t.threshold_id)
                if last is not None and current_time - last < t.cooldown_seconds:
                    continue
                alert = FiredAlert(
                    threshold_id=t.threshold_id, metric_name=metric_name,
                    actual_value=value, threshold_value=t.value,
                    alert_level=t.alert_level, channel=t.escalation_channel,
                    fired_at=current_time,
                )
                self._fired.append(alert)
                self._last_fired[t.threshold_id] = current_time
                alerts_fired.append({
                    "threshold_id": t.threshold_id, "level": t.alert_level,
                    "channel": t.escalation_channel, "value": value,
                    "threshold": t.value,
                })
                logger.warning("usage_alert_fired", threshold=t.threshold_id, value=value)
        return alerts_fired

    def get_fired_alerts(self, level: str | None = None, limit: int = 20) -> list[dict]:
        alerts = list(reversed(self._fired))
        if level:
            alerts = [a for a in alerts if a.alert_level == level]
        return [
            {"threshold_id": a.threshold_id, "metric": a.metric_name,
             "value": a.actual_value, "threshold": a.threshold_value,
             "level": a.alert_level, "channel": a.channel}
            for a in alerts[:limit]
        ]

    def toggle(self, threshold_id: str, enabled: bool) -> dict:
        t = self._thresholds.get(threshold_id)
        if not t:
            raise ValueError(f"Threshold {threshold_id} not found")
        t.enabled = enabled
        return {"threshold_id": threshold_id, "enabled": enabled}

    def list_thresholds(self) -> list[dict]:
        return [
            {"threshold_id": t.threshold_id, "metric": t.metric_name,
             "operator": t.operator, "value": t.value,
             "level": t.alert_level, "enabled": t.enabled}
            for t in self._thresholds.values()
        ]

    def get_stats(self) -> dict:
        by_level = {lvl: sum(1 for a in self._fired if a.alert_level == lvl) for lvl in ALERT_LEVELS}
        return {
            "total_thresholds": len(self._thresholds),
            "enabled": sum(1 for t in self._thresholds.values() if t.enabled),
            "total_fired": len(self._fired),
            "by_level": by_level,
        }

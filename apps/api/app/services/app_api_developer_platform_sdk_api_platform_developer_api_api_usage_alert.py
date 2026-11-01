"""API Usage Alert — configurable alerts on API usage thresholds."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class AlertRule:
    rule_id: str
    metric: str  # "request_count", "error_rate", "latency_p99", "quota_usage"
    operator: str  # "gt", "lt", "gte", "lte"
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown_s: int = 300

@dataclass
class FiredAlert:
    alert_id: str
    rule_id: str
    metric: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    fired_at: float = field(default_factory=time.time)

VALID_METRICS = {"request_count", "error_rate", "latency_p99", "quota_usage"}
VALID_OPS = {"gt", "lt", "gte", "lte"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlert:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], AlertRule] = {}
        self._alerts: dict[str, list[FiredAlert]] = {}
        self._last_fired: dict[tuple[str, str], float] = {}

    def add_rule(self, installation_id: str, rule: AlertRule) -> AlertRule:
        if not installation_id: raise ValueError("installation_id is required")
        if rule.metric not in VALID_METRICS: raise ValueError(f"Invalid metric: {rule.metric}")
        if rule.operator not in VALID_OPS: raise ValueError(f"Invalid operator: {rule.operator}")
        self._rules[(installation_id, rule.rule_id)] = rule
        return rule

    def evaluate(self, installation_id: str, metrics: dict[str, float]) -> list[FiredAlert]:
        fired: list[FiredAlert] = []
        now = time.time()
        for (inst, rid), rule in self._rules.items():
            if inst != installation_id: continue
            val = metrics.get(rule.metric)
            if val is None: continue
            last = self._last_fired.get((installation_id, rid), 0)
            if now - last < rule.cooldown_s: continue
            triggered = False
            if rule.operator == "gt" and val > rule.threshold: triggered = True
            elif rule.operator == "gte" and val >= rule.threshold: triggered = True
            elif rule.operator == "lt" and val < rule.threshold: triggered = True
            elif rule.operator == "lte" and val <= rule.threshold: triggered = True
            if triggered:
                alert = FiredAlert(alert_id=f"a-{rid}-{int(now)}", rule_id=rid, metric=rule.metric, current_value=val, threshold=rule.threshold, severity=rule.severity)
                self._alerts.setdefault(installation_id, []).append(alert)
                self._last_fired[(installation_id, rid)] = now
                fired.append(alert)
        return fired

    def acknowledge(self, installation_id: str, alert_id: str) -> FiredAlert:
        for a in self._alerts.get(installation_id, []):
            if a.alert_id == alert_id:
                a.status = AlertStatus.ACKNOWLEDGED
                return a
        raise KeyError(f"Alert {alert_id} not found")

    def active_alerts(self, installation_id: str) -> list[FiredAlert]:
        return [a for a in self._alerts.get(installation_id, []) if a.status == AlertStatus.ACTIVE]

    def alert_count(self, installation_id: str) -> int:
        return len(self._alerts.get(installation_id, []))

"""API Consumer Usage Alert Rule — configurable alert rules for usage thresholds."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class AlertRule:
    rule_id: str
    consumer_id: str
    metric: str  # "requests", "errors", "latency_p99", "bandwidth"
    condition: str  # "gt", "lt", "gte", "lte"
    threshold: float
    severity: str = "warning"  # "info", "warning", "critical"
    cooldown_minutes: int = 15
    fired_count: int = 0

VALID_METRICS = {"requests", "errors", "latency_p99", "bandwidth", "error_rate", "quota_usage"}
VALID_CONDITIONS = {"gt", "lt", "gte", "lte"}
VALID_SEVERITIES = {"info", "warning", "critical"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRule:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[AlertRule]] = {}

    def add_rule(self, installation_id: str, rule: AlertRule) -> AlertRule:
        if not installation_id: raise ValueError("installation_id is required")
        if rule.metric not in VALID_METRICS: raise ValueError(f"Invalid metric: {rule.metric}")
        if rule.condition not in VALID_CONDITIONS: raise ValueError(f"Invalid condition: {rule.condition}")
        if rule.severity not in VALID_SEVERITIES: raise ValueError(f"Invalid severity: {rule.severity}")
        self._rules.setdefault((installation_id, rule.consumer_id), []).append(rule)
        return rule

    def evaluate(self, installation_id: str, consumer_id: str, metrics: dict[str, float]) -> list[AlertRule]:
        rules = self._rules.get((installation_id, consumer_id), [])
        fired: list[AlertRule] = []
        for r in rules:
            val = metrics.get(r.metric)
            if val is None: continue
            triggered = False
            if r.condition == "gt" and val > r.threshold: triggered = True
            elif r.condition == "gte" and val >= r.threshold: triggered = True
            elif r.condition == "lt" and val < r.threshold: triggered = True
            elif r.condition == "lte" and val <= r.threshold: triggered = True
            if triggered:
                r.fired_count += 1
                fired.append(r)
        return fired

    def list_rules(self, installation_id: str, consumer_id: str | None = None) -> list[AlertRule]:
        if consumer_id:
            return self._rules.get((installation_id, consumer_id), [])
        return [r for (inst, _), rules in self._rules.items() if inst == installation_id for r in rules]

    def rule_count(self, installation_id: str) -> int:
        return sum(len(rs) for (inst, _), rs in self._rules.items() if inst == installation_id)

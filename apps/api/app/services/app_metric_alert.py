"""App Metric Alert — define and evaluate metric-based alerts.

Manages metric alerts:
- Define alert rules with thresholds
- Evaluate metrics against rules
- Track alert state (ok/firing/resolved)
- Per-installation scoped alerts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class AlertState(str, Enum):
    OK = "ok"
    FIRING = "firing"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    """A metric alert rule."""

    rule_id: str
    metric_name: str
    operator: str  # "gt", "lt", "gte", "lte", "eq"
    threshold: float
    severity: str = "warning"  # "info", "warning", "critical"
    state: AlertState = AlertState.OK
    fire_count: int = 0


_OPS = {
    "gt": lambda v, t: v > t,
    "lt": lambda v, t: v < t,
    "gte": lambda v, t: v >= t,
    "lte": lambda v, t: v <= t,
    "eq": lambda v, t: v == t,
}


class AppMetricAlert:
    """Define and evaluate metric-based alerts."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], AlertRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, metric_name: str,
        operator: str, threshold: float, severity: str = "warning",
    ) -> AlertRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if operator not in _OPS:
            raise ValueError(f"operator must be one of {list(_OPS.keys())}")
        if severity not in ("info", "warning", "critical"):
            raise ValueError("severity must be info, warning, or critical")

        rule = AlertRule(
            rule_id=rule_id, metric_name=metric_name,
            operator=operator, threshold=threshold, severity=severity,
        )
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def evaluate(self, installation_id: str, metric_name: str, value: float) -> list[AlertRule]:
        """Evaluate a metric value against all matching rules. Returns firing rules."""
        firing = []
        for (inst, _), rule in self._rules.items():
            if inst != installation_id or rule.metric_name != metric_name:
                continue
            op_fn = _OPS[rule.operator]
            if op_fn(value, rule.threshold):
                if rule.state != AlertState.FIRING:
                    rule.state = AlertState.FIRING
                    rule.fire_count += 1
                firing.append(rule)
            else:
                if rule.state == AlertState.FIRING:
                    rule.state = AlertState.RESOLVED
                elif rule.state != AlertState.RESOLVED:
                    rule.state = AlertState.OK
        return firing

    def firing_alerts(self, installation_id: str) -> list[AlertRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id and r.state == AlertState.FIRING]

    def list_rules(self, installation_id: str) -> list[AlertRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

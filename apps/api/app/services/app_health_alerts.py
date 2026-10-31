"""App health alerting — threshold-based alerts for app health.

Evaluates health scores against configurable thresholds
and generates alerts for developers.
"""

from dataclasses import dataclass


@dataclass
class AlertRule:
    name: str
    metric: str
    operator: str  # gt, lt, gte, lte, eq
    threshold: float
    severity: str  # info, warning, critical


DEFAULT_RULES = [
    AlertRule("high_error_rate", "error_rate_pct", "gte", 10.0, "warning"),
    AlertRule("critical_error_rate", "error_rate_pct", "gte", 25.0, "critical"),
    AlertRule("low_health_score", "score", "lte", 50, "critical"),
    AlertRule("degraded_health", "score", "lte", 80, "warning"),
    AlertRule("high_timeout_rate", "timeout_rate_pct", "gte", 5.0, "warning"),
]


def evaluate_rule(rule: AlertRule, metrics: dict) -> dict | None:
    """Evaluate a single alert rule against metrics. Returns alert or None."""
    value = metrics.get(rule.metric)
    if value is None:
        return None

    triggered = False
    if rule.operator == "gt": triggered = value > rule.threshold
    elif rule.operator == "lt": triggered = value < rule.threshold
    elif rule.operator == "gte": triggered = value >= rule.threshold
    elif rule.operator == "lte": triggered = value <= rule.threshold
    elif rule.operator == "eq": triggered = value == rule.threshold

    if triggered:
        return {
            "rule": rule.name,
            "severity": rule.severity,
            "metric": rule.metric,
            "value": value,
            "threshold": rule.threshold,
            "message": f"{rule.name}: {rule.metric}={value} {rule.operator} {rule.threshold}",
        }
    return None


def check_health_alerts(metrics: dict, rules: list[AlertRule] | None = None) -> list[dict]:
    """Check all alert rules against metrics. Returns triggered alerts."""
    rules = rules or DEFAULT_RULES
    return [alert for rule in rules if (alert := evaluate_rule(rule, metrics)) is not None]

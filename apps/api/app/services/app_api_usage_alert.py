"""App API Usage Alert — alert on usage anomalies.

Manages usage alerts:
- Define alert rules on usage metrics
- Detect spikes and drops
- Track alert history
- Per-installation scoped alerts
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class UsageAlertRule:
    """A usage alert rule."""

    rule_id: str
    metric: str
    condition: str  # "spike", "drop", "exceeds"
    threshold: float
    fired: bool = False
    fire_count: int = 0


class AppAPIUsageAlert:
    """Alert on usage anomalies."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], UsageAlertRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, metric: str,
        condition: str, threshold: float,
    ) -> UsageAlertRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if condition not in ("spike", "drop", "exceeds"):
            raise ValueError("condition must be spike, drop, or exceeds")

        rule = UsageAlertRule(
            rule_id=rule_id, metric=metric,
            condition=condition, threshold=threshold,
        )
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def evaluate(
        self, installation_id: str, metric: str,
        current_value: float, previous_value: float,
    ) -> list[UsageAlertRule]:
        """Evaluate metric against rules. Returns newly fired rules."""
        fired: list[UsageAlertRule] = []
        for (inst, _), rule in self._rules.items():
            if inst != installation_id or rule.metric != metric:
                continue
            triggered = False
            if rule.condition == "exceeds" and current_value > rule.threshold:
                triggered = True
            elif rule.condition == "spike" and previous_value > 0:
                change_pct = ((current_value - previous_value) / previous_value) * 100
                if change_pct > rule.threshold:
                    triggered = True
            elif rule.condition == "drop" and previous_value > 0:
                change_pct = ((previous_value - current_value) / previous_value) * 100
                if change_pct > rule.threshold:
                    triggered = True

            if triggered:
                rule.fired = True
                rule.fire_count += 1
                fired.append(rule)
            else:
                rule.fired = False
        return fired

    def fired_rules(self, installation_id: str) -> list[UsageAlertRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id and r.fired]

    def list_rules(self, installation_id: str) -> list[UsageAlertRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

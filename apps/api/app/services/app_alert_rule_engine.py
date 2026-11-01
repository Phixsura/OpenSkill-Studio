"""App Alert Rule Engine — conditional alerting based on metric thresholds.

Evaluates alert rules against metric values:
- Define rules with conditions (gt, lt, gte, lte, eq)
- Evaluate metrics against rules
- Track alert state: ok → firing → resolved
- Cooldown to prevent alert storms
- Per-installation scoped rules
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class AlertState(str, Enum):
    OK = "ok"
    FIRING = "firing"
    RESOLVED = "resolved"


class Operator(str, Enum):
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"


@dataclass
class AlertRule:
    """An alert rule definition."""

    rule_id: str
    name: str
    metric: str
    operator: Operator
    threshold: float
    cooldown_seconds: float = 300.0
    enabled: bool = True


@dataclass
class AlertEvent:
    """An alert firing or resolution event."""

    rule_id: str
    installation_id: str
    state: AlertState
    value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)


class AppAlertRuleEngine:
    """Conditional alerting based on metric thresholds."""

    def __init__(self) -> None:
        # (installation_id, rule_id) → AlertRule
        self._rules: dict[tuple[str, str], AlertRule] = {}
        # (installation_id, rule_id) → current state
        self._states: dict[tuple[str, str], AlertState] = {}
        # (installation_id, rule_id) → last fired timestamp
        self._last_fired: dict[tuple[str, str], float] = {}
        # Alert history
        self._events: list[AlertEvent] = []

    def add_rule(
        self,
        installation_id: str,
        rule: AlertRule,
    ) -> AlertRule:
        """Add an alert rule."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not rule.rule_id:
            raise ValueError("rule_id is required")

        key = (installation_id, rule.rule_id)
        if key in self._rules:
            raise ValueError(f"Rule {rule.rule_id} already exists")

        self._rules[key] = rule
        self._states[key] = AlertState.OK
        return rule

    def evaluate(
        self,
        installation_id: str,
        metric: str,
        value: float,
        now: float | None = None,
    ) -> list[AlertEvent]:
        """Evaluate a metric value against all matching rules."""
        now = now or time.time()
        events: list[AlertEvent] = []

        for (inst, _), rule in self._rules.items():
            if inst != installation_id or rule.metric != metric or not rule.enabled:
                continue

            key = (installation_id, rule.rule_id)
            triggered = self._check(rule.operator, value, rule.threshold)
            current_state = self._states[key]

            if triggered and current_state == AlertState.OK:
                # Check cooldown
                last = self._last_fired.get(key, 0)
                if now - last < rule.cooldown_seconds:
                    continue

                self._states[key] = AlertState.FIRING
                self._last_fired[key] = now
                event = AlertEvent(
                    rule_id=rule.rule_id, installation_id=installation_id,
                    state=AlertState.FIRING,
                    value=value, threshold=rule.threshold, timestamp=now,
                )
                events.append(event)
                self._events.append(event)

            elif not triggered and current_state == AlertState.FIRING:
                self._states[key] = AlertState.RESOLVED
                event = AlertEvent(
                    rule_id=rule.rule_id, installation_id=installation_id,
                    state=AlertState.RESOLVED,
                    value=value, threshold=rule.threshold, timestamp=now,
                )
                events.append(event)
                self._events.append(event)
                # Reset to OK after resolved
                self._states[key] = AlertState.OK

        return events

    def get_state(self, installation_id: str, rule_id: str) -> AlertState:
        key = (installation_id, rule_id)
        return self._states.get(key, AlertState.OK)

    def list_rules(self, installation_id: str) -> list[AlertRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def get_events(self, installation_id: str, limit: int = 50) -> list[AlertEvent]:
        if not installation_id:
            raise ValueError("installation_id is required")
        matching = [e for e in self._events if e.installation_id == installation_id]
        return list(reversed(matching[-limit:]))

    def _check(self, op: Operator, value: float, threshold: float) -> bool:
        if op == Operator.GT:
            return value > threshold
        if op == Operator.LT:
            return value < threshold
        if op == Operator.GTE:
            return value >= threshold
        if op == Operator.LTE:
            return value <= threshold
        if op == Operator.EQ:
            return value == threshold
        return False

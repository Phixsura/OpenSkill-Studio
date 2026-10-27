"""App Automation Engine — rule-based event-to-action automation for installed apps.

Enables no-code automation rules within the developer platform:
- IF event matches condition THEN execute action
- Condition types: field equals, contains, regex, exists, threshold
- Action types: webhook, notification, set_field, log
- Rule chaining with AND/OR logic
- Execution history with success/failure tracking
- Dry-run mode for testing rules
- Per-app rule limits
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()

MAX_RULES_PER_APP = 50


class ConditionOp(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    REGEX = "regex"
    EXISTS = "exists"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"


class ActionType(str, Enum):
    WEBHOOK = "webhook"
    NOTIFICATION = "notification"
    SET_FIELD = "set_field"
    LOG = "log"


class LogicOp(str, Enum):
    AND = "and"
    OR = "or"


@dataclass
class Condition:
    """A single condition to evaluate against event data."""

    field: str           # dot-path e.g. "data.score"
    op: ConditionOp
    value: str | None = None  # expected value (not needed for EXISTS)


@dataclass
class Action:
    """An action to execute when conditions are met."""

    action_type: ActionType
    config: dict = field(default_factory=dict)
    # WEBHOOK: {"url": "...", "method": "POST"}
    # NOTIFICATION: {"title": "...", "body": "...", "priority": "info"}
    # SET_FIELD: {"field": "status", "value": "flagged"}
    # LOG: {"message": "..."}


@dataclass
class AutomationRule:
    """A complete automation rule."""

    rule_id: str
    app_id: str
    org_id: str              # mandatory: installation scope, set server-side
    name: str
    event_type: str          # e.g. "submission.graded"
    conditions: list[Condition]
    logic: LogicOp = LogicOp.AND
    actions: list[Action] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ExecutionResult:
    """Result of executing or evaluating a rule."""

    rule_id: str
    matched: bool
    actions_executed: int = 0
    dry_run: bool = False
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


def _get_nested(data: dict, path: str) -> object:
    """Get a nested value by dot-path. Returns None if not found."""
    parts = path.split(".")
    current: object = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def evaluate_condition(condition: Condition, event_data: dict) -> bool:
    """Evaluate a single condition against event data."""
    actual = _get_nested(event_data, condition.field)

    if condition.op == ConditionOp.EXISTS:
        return actual is not None

    if actual is None:
        return False

    actual_str = str(actual)
    expected = condition.value or ""

    if condition.op == ConditionOp.EQUALS:
        return actual_str == expected
    elif condition.op == ConditionOp.NOT_EQUALS:
        return actual_str != expected
    elif condition.op == ConditionOp.CONTAINS:
        return expected in actual_str
    elif condition.op == ConditionOp.REGEX:
        try:
            return bool(re.search(expected, actual_str))
        except re.error:
            return False
    elif condition.op in (ConditionOp.GT, ConditionOp.LT, ConditionOp.GTE, ConditionOp.LTE):
        try:
            a = float(actual_str)
            b = float(expected)
            if condition.op == ConditionOp.GT:
                return a > b
            elif condition.op == ConditionOp.LT:
                return a < b
            elif condition.op == ConditionOp.GTE:
                return a >= b
            elif condition.op == ConditionOp.LTE:
                return a <= b
        except ValueError:
            return False

    return False


class AppAutomationEngine:
    """Rule-based automation engine."""

    def __init__(self):
        self._rules: dict[str, AutomationRule] = {}
        self._history: list[ExecutionResult] = []
        self._next_id = 0

    # ── Rule CRUD ────────────────────────────────────────

    def add_rule(self, app_id: str, org_id: str, name: str, event_type: str,
                 conditions: list[Condition], actions: list[Action],
                 logic: LogicOp = LogicOp.AND) -> AutomationRule | str:
        """Add a rule. org_id is set server-side from the installation."""
        if not org_id:
            return "org_id is required"
        app_rules = [r for r in self._rules.values() if r.app_id == app_id]
        if len(app_rules) >= MAX_RULES_PER_APP:
            return f"Rule limit reached: {MAX_RULES_PER_APP} per app"
        if not conditions:
            return "At least one condition is required"
        if not actions:
            return "At least one action is required"

        self._next_id += 1
        rule_id = f"rule-{self._next_id}"
        rule = AutomationRule(
            rule_id=rule_id, app_id=app_id, org_id=org_id, name=name,
            event_type=event_type, conditions=conditions,
            logic=logic, actions=actions,
        )
        self._rules[rule_id] = rule
        return rule

    def update_rule(self, app_id: str, org_id: str, rule_id: str, enabled: bool | None = None,
                    name: str | None = None) -> AutomationRule | None:
        """Update a rule. Requires app_id ownership to prevent IDOR."""
        rule = self._rules.get(rule_id)
        if rule is None or rule.app_id != app_id or rule.org_id != org_id:
            return None
        if enabled is not None:
            rule.enabled = enabled
        if name is not None:
            rule.name = name
        return rule

    def delete_rule(self, app_id: str, org_id: str, rule_id: str) -> bool:
        """Delete a rule. Requires app_id ownership to prevent IDOR."""
        rule = self._rules.get(rule_id)
        if rule is None or rule.app_id != app_id or rule.org_id != org_id:
            return False
        del self._rules[rule_id]
        return True

    def get_rule(self, app_id: str, org_id: str, rule_id: str) -> AutomationRule | None:
        """Get a rule. Requires app_id ownership to prevent IDOR."""
        rule = self._rules.get(rule_id)
        if rule is None or rule.app_id != app_id or rule.org_id != org_id:
            return None
        return rule

    def list_rules(self, app_id: str, org_id: str) -> list[AutomationRule]:
        """List rules scoped to app_id + org_id."""
        return sorted(
            [r for r in self._rules.values() if r.app_id == app_id and r.org_id == org_id],
            key=lambda r: r.created_at,
        )

    # ── Execution ────────────────────────────────────────

    def process_event(self, event_type: str, event_data: dict,
                      org_id: str,
                      dry_run: bool = False) -> list[ExecutionResult]:
        """Process an event against all matching enabled rules.

        org_id is mandatory and scopes execution to that org's rules only.
        """
        if not org_id:
            raise ValueError("org_id is required for event processing")

        results: list[ExecutionResult] = []

        for rule in self._rules.values():
            if not rule.enabled or rule.event_type != event_type:
                continue
            # Cross-tenant isolation: skip rules from other orgs
            if rule.org_id != org_id:
                continue

            matched = self._evaluate_rule(rule, event_data)
            actions_executed = 0

            if matched and not dry_run:
                for action in rule.actions:
                    self._execute_action(action, event_data)
                    actions_executed += 1

            result = ExecutionResult(
                rule_id=rule.rule_id,
                matched=matched,
                actions_executed=actions_executed if not dry_run else 0,
                dry_run=dry_run,
            )
            results.append(result)
            self._history.append(result)

        return results

    def get_history(self, app_id: str, org_id: str, limit: int = 50) -> list[ExecutionResult]:
        """Get execution history scoped to app_id + org_id."""
        rule_ids = {r.rule_id for r in self._rules.values()
                    if r.app_id == app_id and r.org_id == org_id}
        if not rule_ids:
            return []
        entries = self._history
        if rule_ids:
            entries = [e for e in entries if e.rule_id in rule_ids]
        return entries[-limit:]

    # ── Internal ─────────────────────────────────────────

    @staticmethod
    def _evaluate_rule(rule: AutomationRule, event_data: dict) -> bool:
        results = [evaluate_condition(c, event_data) for c in rule.conditions]
        if rule.logic == LogicOp.AND:
            return all(results)
        return any(results)

    @staticmethod
    def _execute_action(action: Action, event_data: dict) -> None:
        """Execute a single action (stub — real impl would call webhooks, etc.)."""
        log.info("automation.action_executed",
                 action_type=action.action_type.value,
                 config=action.config)

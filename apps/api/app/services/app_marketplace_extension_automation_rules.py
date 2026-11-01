"""Automation Rules — if/then rule engine for extension workflow automation.

Define rules with conditions and actions that trigger automatically on
events, with support for AND/OR logic, action chaining, and dry-run mode.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from enum import Enum


class ConditionOp(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EXISTS = "exists"


class LogicOp(str, Enum):
    AND = "and"
    OR = "or"


@dataclass
class Condition:
    field: str
    operator: ConditionOp
    value: str = ""


@dataclass
class Action:
    action_type: str  # e.g. "send_notification", "update_status", "call_webhook"
    params: dict = field(default_factory=dict)


@dataclass
class AutomationRule:
    rule_id: str
    extension_id: str
    name: str
    event_type: str
    logic: LogicOp = LogicOp.AND
    conditions: list[Condition] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    enabled: bool = True
    execution_count: int = 0
    last_triggered: str = ""


@dataclass
class RuleEvaluation:
    rule_id: str
    matched: bool
    conditions_met: list[bool]
    actions_executed: list[str]
    dry_run: bool = False


class AutomationRuleService:
    """Evaluates and executes if/then automation rules."""

    def __init__(self):
        self._rules: dict[str, AutomationRule] = {}

    def create_rule(self, extension_id: str, name: str, event_type: str,
                    conditions: list[dict], actions: list[dict],
                    logic: LogicOp = LogicOp.AND) -> AutomationRule:
        rule_id = f"ar_{secrets.token_urlsafe(8)}"
        parsed_conditions = [
            Condition(field=c["field"], operator=ConditionOp(c["operator"]),
                      value=str(c.get("value", "")))
            for c in conditions
        ]
        parsed_actions = [Action(action_type=a["type"], params=a.get("params", {})) for a in actions]

        rule = AutomationRule(
            rule_id=rule_id, extension_id=extension_id, name=name,
            event_type=event_type, logic=logic,
            conditions=parsed_conditions, actions=parsed_actions,
        )
        self._rules[rule_id] = rule
        return rule

    def _eval_condition(self, condition: Condition, event_data: dict) -> bool:
        value = event_data.get(condition.field)
        if condition.operator == ConditionOp.EXISTS:
            return value is not None
        if value is None:
            return False
        sval = str(value)
        if condition.operator == ConditionOp.EQUALS:
            return sval == condition.value
        elif condition.operator == ConditionOp.NOT_EQUALS:
            return sval != condition.value
        elif condition.operator == ConditionOp.CONTAINS:
            return condition.value in sval
        elif condition.operator == ConditionOp.GREATER_THAN:
            try:
                return float(sval) > float(condition.value)
            except ValueError:
                return False
        elif condition.operator == ConditionOp.LESS_THAN:
            try:
                return float(sval) < float(condition.value)
            except ValueError:
                return False
        return False

    def evaluate(self, extension_id: str, event_type: str,
                 event_data: dict, dry_run: bool = False) -> list[RuleEvaluation]:
        rules = [r for r in self._rules.values()
                 if r.extension_id == extension_id
                 and r.event_type == event_type and r.enabled]

        results: list[RuleEvaluation] = []
        for rule in rules:
            cond_results = [self._eval_condition(c, event_data) for c in rule.conditions]

            if rule.logic == LogicOp.AND:
                matched = all(cond_results) if cond_results else True
            else:
                matched = any(cond_results) if cond_results else False

            actions_executed = []
            if matched and not dry_run:
                rule.execution_count += 1
                from datetime import datetime, timezone
                rule.last_triggered = datetime.now(timezone.utc).isoformat()
                actions_executed = [a.action_type for a in rule.actions]

            results.append(RuleEvaluation(
                rule_id=rule.rule_id, matched=matched,
                conditions_met=cond_results, actions_executed=actions_executed,
                dry_run=dry_run,
            ))

        return results

    def toggle(self, rule_id: str) -> bool:
        rule = self._rules.get(rule_id)
        if rule:
            rule.enabled = not rule.enabled
            return True
        return False

    def list_rules(self, extension_id: str) -> list[AutomationRule]:
        return [r for r in self._rules.values() if r.extension_id == extension_id]

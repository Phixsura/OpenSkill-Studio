"""Policy Engine — evaluate and enforce marketplace governance rules.

Provides a rule engine for marketplace policies: auto-approve criteria,
suspension triggers, quality gates, and developer reputation scoring.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_REVIEW = "require_review"
    WARN = "warn"


@dataclass
class PolicyRule:
    rule_id: str
    name: str
    condition: str  # field.operator.value e.g. "rating.gte.3.0"
    action: PolicyAction
    message: str = ""
    priority: int = 0


@dataclass
class PolicyEvaluation:
    rule_id: str
    rule_name: str
    matched: bool
    action: PolicyAction
    message: str


class PolicyEngine:
    """Evaluates marketplace governance policies."""

    def __init__(self):
        self._rules: list[PolicyRule] = []

    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, rule_id: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        return len(self._rules) < before

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        """Evaluate a condition like 'rating.gte.3.0' against context."""
        parts = condition.split(".", 2)
        if len(parts) < 3:
            return False
        field_name, operator, value_str = parts[0], parts[1], parts[2]
        actual = context.get(field_name)
        if actual is None:
            return False

        try:
            if operator == "gte":
                return float(actual) >= float(value_str)
            elif operator == "lte":
                return float(actual) <= float(value_str)
            elif operator == "gt":
                return float(actual) > float(value_str)
            elif operator == "lt":
                return float(actual) < float(value_str)
            elif operator == "eq":
                return str(actual) == value_str
            elif operator == "neq":
                return str(actual) != value_str
            elif operator == "in":
                return str(actual) in value_str.split(",")
            elif operator == "contains":
                return value_str in str(actual)
        except (ValueError, TypeError):
            return False
        return False

    def evaluate(self, context: dict) -> list[PolicyEvaluation]:
        """Evaluate all rules against a context dict."""
        results = []
        for rule in self._rules:
            matched = self._evaluate_condition(rule.condition, context)
            results.append(PolicyEvaluation(
                rule_id=rule.rule_id, rule_name=rule.name,
                matched=matched, action=rule.action if matched else PolicyAction.ALLOW,
                message=rule.message if matched else "",
            ))
        return results

    def decide(self, context: dict) -> tuple[PolicyAction, list[str]]:
        """Get final decision: highest-priority matching rule wins."""
        evals = self.evaluate(context)
        matched = [e for e in evals if e.matched]
        if not matched:
            return PolicyAction.ALLOW, []
        # Highest priority matched rule (already sorted)
        top = matched[0]
        reasons = [e.message for e in matched if e.message]
        return top.action, reasons

    def list_rules(self) -> list[PolicyRule]:
        return list(self._rules)

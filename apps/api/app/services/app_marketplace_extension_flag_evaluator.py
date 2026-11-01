"""Feature Flag Evaluator — multi-condition targeting with rule precedence.

Implements:
- Rule-based targeting: user attributes matched against conditions
- Operators: eq, ne, in, not_in, gt, lt, contains, starts_with, regex
- Rule precedence: first matching rule wins
- Default fallback when no rules match
- Percentage-based gradual rollout within rules
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import hashlib


@dataclass
class Condition:
    attribute: str
    operator: str  # eq, ne, in, not_in, gt, lt, contains, starts_with, regex
    value: object   # string, number, list depending on operator


@dataclass
class TargetingRule:
    name: str
    conditions: list[Condition]
    variation: str  # "on", "off", or custom variation
    rollout_pct: int = 100  # 0-100, percentage of matched users


@dataclass
class FlagConfig:
    flag_key: str
    enabled: bool = True
    default_variation: str = "off"
    rules: list[TargetingRule] = field(default_factory=list)


class FlagEvaluatorService:
    def __init__(self):
        self._flags: dict[str, FlagConfig] = {}

    def register(self, flag_key: str, default: str = "off",
                 rules: list[TargetingRule] | None = None) -> FlagConfig:
        config = FlagConfig(flag_key=flag_key, default_variation=default,
                            rules=rules or [])
        self._flags[flag_key] = config
        return config

    def evaluate(self, flag_key: str, user_attrs: dict) -> str:
        """Evaluate flag for a user. Returns variation string."""
        config = self._flags.get(flag_key)
        if not config or not config.enabled:
            return config.default_variation if config else "off"

        for rule in config.rules:
            if self._matches_rule(rule, user_attrs):
                # Check rollout percentage
                if rule.rollout_pct < 100:
                    user_id = str(user_attrs.get("user_id", ""))
                    bucket = self._hash_bucket(flag_key, user_id)
                    if bucket >= rule.rollout_pct:
                        continue  # not in rollout
                return rule.variation

        return config.default_variation

    def _matches_rule(self, rule: TargetingRule, attrs: dict) -> bool:
        return all(self._eval_condition(c, attrs) for c in rule.conditions)

    def _eval_condition(self, cond: Condition, attrs: dict) -> bool:
        actual = attrs.get(cond.attribute)
        if actual is None:
            return cond.operator == "ne"  # None != anything is True

        op = cond.operator
        expected = cond.value

        if op == "eq":
            return actual == expected
        elif op == "ne":
            return actual != expected
        elif op == "in":
            return actual in expected  # expected is a list
        elif op == "not_in":
            return actual not in expected
        elif op == "gt":
            return isinstance(actual, (int, float)) and actual > expected
        elif op == "lt":
            return isinstance(actual, (int, float)) and actual < expected
        elif op == "contains":
            return isinstance(actual, str) and expected in actual
        elif op == "starts_with":
            return isinstance(actual, str) and actual.startswith(expected)
        elif op == "regex":
            return isinstance(actual, str) and bool(re.search(expected, actual))
        return False

    def _hash_bucket(self, flag_key: str, user_id: str) -> int:
        h = hashlib.md5(f"{flag_key}:{user_id}".encode()).hexdigest()
        return int(h[:8], 16) % 100

    def evaluate_all(self, user_attrs: dict) -> dict[str, str]:
        return {key: self.evaluate(key, user_attrs) for key in self._flags}

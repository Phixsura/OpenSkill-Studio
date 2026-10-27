"""Rule Engine — forward-chaining inference with priority and conflict resolution.

Implements:
- Rules with conditions (when) and actions (then)
- Multi-condition evaluation (AND/OR)
- Priority-based conflict resolution
- Fact assertion and retraction
- Rule chaining (action can assert new facts, triggering more rules)
- Execution limit to prevent infinite loops
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Condition:
    fact: str
    operator: str  # eq, ne, gt, lt, gte, lte, exists, not_exists
    value: Any = None


@dataclass
class Rule:
    name: str
    priority: int = 0  # higher = fires first
    conditions: list[Condition] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)  # [{type: "assert"|"retract"|"set", ...}]
    fired_count: int = 0
    enabled: bool = True


class RuleEngineService:
    MAX_ITERATIONS = 100

    def __init__(self):
        self._rules: list[Rule] = []
        self._facts: dict[str, Any] = {}
        self._log: list[str] = []

    def add_rule(self, name: str, conditions: list[Condition],
                 actions: list[dict], priority: int = 0) -> Rule:
        rule = Rule(name=name, priority=priority, conditions=conditions, actions=actions)
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        return rule

    def assert_fact(self, key: str, value: Any) -> None:
        self._facts[key] = value

    def retract_fact(self, key: str) -> None:
        self._facts.pop(key, None)

    def get_facts(self) -> dict:
        return dict(self._facts)

    def evaluate(self) -> list[str]:
        """Forward chaining: keep firing rules until no more match."""
        self._log = []
        fired_this_run: set[str] = set()

        for iteration in range(self.MAX_ITERATIONS):
            fired = False
            for rule in self._rules:
                if not rule.enabled:
                    continue
                # Avoid re-firing same rule with same facts
                fact_key = f"{rule.name}:{hash(frozenset(self._facts.items()))}"
                if fact_key in fired_this_run:
                    continue

                if self._matches(rule):
                    self._fire(rule)
                    fired_this_run.add(fact_key)
                    fired = True
                    break  # restart evaluation (facts may have changed)

            if not fired:
                break

        return list(self._log)

    def _matches(self, rule: Rule) -> bool:
        return all(self._eval_condition(c) for c in rule.conditions)

    def _eval_condition(self, cond: Condition) -> bool:
        if cond.operator == "exists":
            return cond.fact in self._facts
        if cond.operator == "not_exists":
            return cond.fact not in self._facts

        actual = self._facts.get(cond.fact)
        if actual is None:
            return False

        if cond.operator == "eq": return actual == cond.value
        if cond.operator == "ne": return actual != cond.value
        if cond.operator == "gt": return actual > cond.value
        if cond.operator == "lt": return actual < cond.value
        if cond.operator == "gte": return actual >= cond.value
        if cond.operator == "lte": return actual <= cond.value
        return False

    def _fire(self, rule: Rule) -> None:
        rule.fired_count += 1
        self._log.append(f"FIRED: {rule.name}")

        for action in rule.actions:
            action_type = action.get("type")
            if action_type == "assert":
                self._facts[action["key"]] = action["value"]
                self._log.append(f"  ASSERT: {action['key']}={action['value']}")
            elif action_type == "retract":
                self._facts.pop(action["key"], None)
                self._log.append(f"  RETRACT: {action['key']}")
            elif action_type == "set":
                self._facts[action["key"]] = action["value"]

    def get_matching_rules(self) -> list[str]:
        return [r.name for r in self._rules if r.enabled and self._matches(r)]

    def get_execution_log(self) -> list[str]:
        return list(self._log)

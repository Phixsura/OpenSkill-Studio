"""App Response Transform — transform API response shapes.

Manages response transformations:
- Field renaming rules
- Field removal (redaction)
- Default value injection
- Per-installation scoped transforms
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class TransformRule:
    """A response transformation rule."""

    rule_id: str
    action: str  # "rename", "remove", "default"
    field: str  # dot-path
    value: str = ""  # new name for rename, default value for default


class AppResponseTransform:
    """Transform API response shapes."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], TransformRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, action: str,
        field: str, value: str = "",
    ) -> TransformRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if action not in ("rename", "remove", "default"):
            raise ValueError("action must be rename, remove, or default")
        if action == "rename" and not value:
            raise ValueError("rename requires a new field name")

        rule = TransformRule(rule_id=rule_id, action=action, field=field, value=value)
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def apply(self, installation_id: str, response: dict) -> dict:
        """Apply all rules to a response dict. Returns new dict."""
        result = dict(response)
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]

        for rule in rules:
            if rule.action == "rename" and rule.field in result:
                result[rule.value] = result.pop(rule.field)
            elif rule.action == "remove" and rule.field in result:
                del result[rule.field]
            elif rule.action == "default" and rule.field not in result:
                result[rule.field] = rule.value

        return result

    def remove_rule(self, installation_id: str, rule_id: str) -> bool:
        key = (installation_id, rule_id)
        if key in self._rules:
            del self._rules[key]
            return True
        return False

    def list_rules(self, installation_id: str) -> list[TransformRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

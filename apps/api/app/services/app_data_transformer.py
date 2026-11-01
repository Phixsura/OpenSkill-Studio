"""App Data Transformer — apply transformation rules to data records.

Manages data transformations for installed apps:
- Define transformation rules (rename, map, filter, compute)
- Apply transforms to records
- Chain multiple transforms
- Per-installation scoped rule sets
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TransformRule:
    """A single transformation rule."""

    rule_id: str
    rule_type: str  # "rename", "map_value", "filter", "compute", "default"
    source_field: str
    target_field: str = ""
    mapping: dict | None = None  # for map_value
    expression: str = ""  # for compute (simple: "field1 + field2")
    default_value: object = None


class AppDataTransformer:
    """Apply transformation rules to data records."""

    def __init__(self) -> None:
        # (installation_id, ruleset_id) → list[TransformRule]
        self._rulesets: dict[tuple[str, str], list[TransformRule]] = {}

    def define_ruleset(
        self,
        installation_id: str,
        ruleset_id: str,
        rules: list[TransformRule],
    ) -> list[TransformRule]:
        """Define a named set of transformation rules."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not ruleset_id:
            raise ValueError("ruleset_id is required")
        if not rules:
            raise ValueError("at least one rule is required")

        key = (installation_id, ruleset_id)
        self._rulesets[key] = list(rules)
        return rules

    def transform(
        self,
        installation_id: str,
        ruleset_id: str,
        record: dict,
    ) -> dict:
        """Apply a ruleset to a single record."""
        key = (installation_id, ruleset_id)
        rules = self._rulesets.get(key)
        if rules is None:
            raise KeyError(f"Ruleset {ruleset_id} not found")

        result = dict(record)
        for rule in rules:
            result = self._apply_rule(rule, result)
        return result

    def transform_batch(
        self,
        installation_id: str,
        ruleset_id: str,
        records: list[dict],
    ) -> list[dict]:
        """Apply a ruleset to multiple records."""
        return [self.transform(installation_id, ruleset_id, r) for r in records]

    def list_rulesets(self, installation_id: str) -> list[str]:
        return [
            rid for (inst, rid) in self._rulesets if inst == installation_id
        ]

    def get_ruleset(self, installation_id: str, ruleset_id: str) -> list[TransformRule]:
        key = (installation_id, ruleset_id)
        rules = self._rulesets.get(key)
        if rules is None:
            raise KeyError(f"Ruleset {ruleset_id} not found")
        return list(rules)

    def _apply_rule(self, rule: TransformRule, record: dict) -> dict:
        if rule.rule_type == "rename":
            if rule.source_field in record:
                record[rule.target_field] = record.pop(rule.source_field)

        elif rule.rule_type == "map_value":
            if rule.mapping and rule.source_field in record:
                val = record[rule.source_field]
                target = rule.target_field or rule.source_field
                record[target] = rule.mapping.get(str(val), val)

        elif rule.rule_type == "filter":
            # Remove a field
            record.pop(rule.source_field, None)

        elif rule.rule_type == "default":
            if rule.source_field not in record or record[rule.source_field] is None:
                record[rule.source_field] = rule.default_value

        elif rule.rule_type == "compute":
            # Simple concat: "field1 + field2" → concatenate string values
            if " + " in rule.expression:
                parts = rule.expression.split(" + ")
                vals = [str(record.get(p.strip(), "")) for p in parts]
                record[rule.target_field] = " ".join(v for v in vals if v)

        return record

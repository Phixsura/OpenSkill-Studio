"""App API Config Validation — validate app configurations.

Manages config validation:
- Define validation rules per config key
- Validate configs against rules
- Report validation errors
- Per-installation scoped validators
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ConfigValidationRule:
    """A config validation rule."""

    key: str
    rule_type: str  # "required", "regex", "min", "max", "enum"
    value: str  # pattern, min/max value, or comma-separated enums


class AppAPIConfigValidation:
    """Validate app configurations."""

    def __init__(self) -> None:
        self._rules: dict[str, list[ConfigValidationRule]] = {}

    def add_rule(
        self, installation_id: str, key: str, rule_type: str, value: str = "",
    ) -> ConfigValidationRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if rule_type not in ("required", "regex", "min", "max", "enum"):
            raise ValueError("invalid rule_type")

        rule = ConfigValidationRule(key=key, rule_type=rule_type, value=value)
        self._rules.setdefault(installation_id, []).append(rule)
        return rule

    def validate(self, installation_id: str, config: dict[str, str]) -> list[str]:
        """Validate config dict. Returns list of error messages."""
        errors: list[str] = []
        rules = self._rules.get(installation_id, [])

        for rule in rules:
            if rule.rule_type == "required" and rule.key not in config:
                errors.append(f"Missing required key: {rule.key}")
            elif rule.rule_type == "enum" and rule.key in config:
                allowed = [v.strip() for v in rule.value.split(",")]
                if config[rule.key] not in allowed:
                    errors.append(f"{rule.key}: must be one of {allowed}")
            elif rule.rule_type == "min" and rule.key in config:
                try:
                    if float(config[rule.key]) < float(rule.value):
                        errors.append(f"{rule.key}: must be >= {rule.value}")
                except ValueError:
                    errors.append(f"{rule.key}: must be numeric")
            elif rule.rule_type == "max" and rule.key in config:
                try:
                    if float(config[rule.key]) > float(rule.value):
                        errors.append(f"{rule.key}: must be <= {rule.value}")
                except ValueError:
                    errors.append(f"{rule.key}: must be numeric")

        return errors

    def list_rules(self, installation_id: str) -> list[ConfigValidationRule]:
        return self._rules.get(installation_id, [])

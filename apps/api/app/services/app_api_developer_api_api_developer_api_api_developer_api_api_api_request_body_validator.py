"""App API Developer Request Body Validator — validate request bodies against rules."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ValidationRule:
    field: str
    rule_type: str  # "required", "max_length", "min_value", "max_value", "pattern", "type"
    value: str  # rule parameter

@dataclass
class BodyValidationResult:
    endpoint: str
    valid: bool
    errors: list[str] = field(default_factory=list)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidator:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[ValidationRule]] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def add_rule(self, installation_id: str, endpoint: str, field: str, rule_type: str, value: str) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        valid_types = {"required", "max_length", "min_value", "max_value", "pattern", "type"}
        if rule_type not in valid_types: raise ValueError(f"Invalid rule type: {rule_type}")
        key = (installation_id, endpoint)
        self._rules.setdefault(key, []).append(ValidationRule(field=field, rule_type=rule_type, value=value))

    def validate(self, installation_id: str, endpoint: str, body: dict) -> BodyValidationResult:
        key = (installation_id, endpoint)
        rules = self._rules.get(key, [])
        errors: list[str] = []
        for rule in rules:
            val = body.get(rule.field)
            if rule.rule_type == "required" and val is None:
                errors.append(f"{rule.field} is required")
            elif rule.rule_type == "max_length" and isinstance(val, str) and len(val) > int(rule.value):
                errors.append(f"{rule.field} exceeds max length {rule.value}")
            elif rule.rule_type == "min_value" and isinstance(val, (int, float)) and val < float(rule.value):
                errors.append(f"{rule.field} below minimum {rule.value}")
            elif rule.rule_type == "max_value" and isinstance(val, (int, float)) and val > float(rule.value):
                errors.append(f"{rule.field} exceeds maximum {rule.value}")
            elif rule.rule_type == "type":
                expected = {"string": str, "int": int, "float": (int, float), "bool": bool}
                if val is not None and not isinstance(val, expected.get(rule.value, object)):
                    errors.append(f"{rule.field} must be {rule.value}")
        stats = self._stats.setdefault(installation_id, {"total": 0, "invalid": 0})
        stats["total"] += 1
        if errors: stats["invalid"] += 1
        return BodyValidationResult(endpoint=endpoint, valid=len(errors) == 0, errors=errors)

    def stats(self, installation_id: str) -> dict[str, int]:
        return dict(self._stats.get(installation_id, {"total": 0, "invalid": 0}))

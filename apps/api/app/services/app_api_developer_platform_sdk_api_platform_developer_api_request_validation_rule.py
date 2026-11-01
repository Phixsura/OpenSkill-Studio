"""API Request Validation Rule — define and enforce request validation rules."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class ValidationRule:
    rule_id: str
    field_name: str
    rule_type: str  # "required", "regex", "min_length", "max_length", "enum", "type"
    config: dict[str, object] = field(default_factory=dict)
    error_message: str = ""

@dataclass
class ValidationError:
    field: str
    rule_id: str
    message: str

VALID_RULE_TYPES = {"required", "regex", "min_length", "max_length", "enum", "type"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRule:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[ValidationRule]] = {}

    def add_rule(self, installation_id: str, endpoint: str, rule: ValidationRule) -> ValidationRule:
        if not installation_id: raise ValueError("installation_id is required")
        if rule.rule_type not in VALID_RULE_TYPES: raise ValueError(f"Invalid rule type: {rule.rule_type}")
        if rule.rule_type == "regex":
            pattern = rule.config.get("pattern", "")
            if not pattern: raise ValueError("regex rule requires pattern config")
            re.compile(str(pattern))  # validate regex
        self._rules.setdefault((installation_id, endpoint), []).append(rule)
        return rule

    def validate(self, installation_id: str, endpoint: str, request_body: dict) -> list[ValidationError]:
        rules = self._rules.get((installation_id, endpoint), [])
        errors: list[ValidationError] = []
        for r in rules:
            val = request_body.get(r.field_name)
            msg = r.error_message or f"Validation failed for {r.field_name}"
            if r.rule_type == "required" and val is None:
                errors.append(ValidationError(r.field_name, r.rule_id, msg))
            elif r.rule_type == "regex" and val is not None:
                if not re.match(str(r.config.get("pattern", "")), str(val)):
                    errors.append(ValidationError(r.field_name, r.rule_id, msg))
            elif r.rule_type == "min_length" and val is not None:
                if len(str(val)) < int(r.config.get("min", 0)):
                    errors.append(ValidationError(r.field_name, r.rule_id, msg))
            elif r.rule_type == "max_length" and val is not None:
                if len(str(val)) > int(r.config.get("max", 9999)):
                    errors.append(ValidationError(r.field_name, r.rule_id, msg))
            elif r.rule_type == "enum" and val is not None:
                allowed = r.config.get("values", [])
                if val not in allowed:
                    errors.append(ValidationError(r.field_name, r.rule_id, msg))
            elif r.rule_type == "type" and val is not None:
                expected = str(r.config.get("expected", ""))
                type_map = {"string": str, "int": int, "float": (int, float), "bool": bool, "list": list}
                if expected in ("int", "float") and isinstance(val, bool):
                    errors.append(ValidationError(r.field_name, r.rule_id, msg))
                elif expected in type_map and not isinstance(val, type_map[expected]):
                    errors.append(ValidationError(r.field_name, r.rule_id, msg))
        return errors

    def rules_for(self, installation_id: str, endpoint: str) -> list[ValidationRule]:
        return self._rules.get((installation_id, endpoint), [])

    def rule_count(self, installation_id: str) -> int:
        return sum(len(rs) for (inst, _), rs in self._rules.items() if inst == installation_id)

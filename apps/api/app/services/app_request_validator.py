"""App Request Validator — validate incoming API requests.

Validates incoming requests:
- Required header checks
- Content-type validation
- Request size limits
- Custom validation rules
- Per-installation scoped validators
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ValidationError:
    """A validation error."""

    field: str
    message: str
    code: str = "invalid"


@dataclass
class ValidatorRule:
    """A request validation rule."""

    rule_id: str
    rule_type: str  # "required_header", "content_type", "max_size", "path_regex"
    value: str
    enabled: bool = True


@dataclass
class ValidationResult:
    """Result of request validation."""

    valid: bool
    errors: list[ValidationError]


class AppRequestValidator:
    """Validate incoming API requests."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], ValidatorRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, rule_type: str, value: str,
    ) -> ValidatorRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if rule_type not in ("required_header", "content_type", "max_size"):
            raise ValueError(f"Unknown rule_type: {rule_type}")

        rule = ValidatorRule(rule_id=rule_id, rule_type=rule_type, value=value)
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def validate(
        self, installation_id: str, headers: dict[str, str],
        content_type: str = "", body_size: int = 0,
    ) -> ValidationResult:
        errors: list[ValidationError] = []
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id and r.enabled]

        for rule in rules:
            if rule.rule_type == "required_header":
                header_name = rule.value.lower()
                if not any(k.lower() == header_name for k in headers):
                    errors.append(ValidationError(
                        field=rule.value, message=f"Missing required header: {rule.value}",
                        code="missing_header",
                    ))
            elif rule.rule_type == "content_type":
                allowed = [ct.strip() for ct in rule.value.split(",")]
                if content_type and content_type not in allowed:
                    errors.append(ValidationError(
                        field="Content-Type", message=f"Content-Type must be one of: {rule.value}",
                        code="invalid_content_type",
                    ))
            elif rule.rule_type == "max_size":
                max_bytes = int(rule.value)
                if body_size > max_bytes:
                    errors.append(ValidationError(
                        field="body", message=f"Body size {body_size} exceeds limit {max_bytes}",
                        code="body_too_large",
                    ))

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def toggle(self, installation_id: str, rule_id: str, enabled: bool) -> ValidatorRule:
        r = self._get(installation_id, rule_id)
        r.enabled = enabled
        return r

    def list_rules(self, installation_id: str) -> list[ValidatorRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def _get(self, installation_id: str, rule_id: str) -> ValidatorRule:
        key = (installation_id, rule_id)
        r = self._rules.get(key)
        if r is None:
            raise KeyError(f"Rule {rule_id} not found")
        return r

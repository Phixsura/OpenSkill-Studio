"""Sandbox Input Validator — validate and sanitize user inputs for extensions.

Validates input data against rules with type checking, string patterns,
range constraints, XSS sanitization, and custom validators.
"""
from __future__ import annotations
import html
import re
from dataclasses import dataclass, field


@dataclass
class ValidationRule:
    field: str
    rule_type: str  # required, type, min, max, pattern, enum, maxlen, minlen
    value: str | int | float | list = ""
    message: str = ""


@dataclass
class ValidationError:
    field: str
    message: str
    rule: str


XSS_PATTERNS = [
    re.compile(r"<script", re.I),
    re.compile(r"javascript:", re.I),
    re.compile(r"on\w+=", re.I),
    re.compile(r"<iframe", re.I),
]


class SandboxInputValidatorService:
    """Validates and sanitizes extension input data."""

    def validate(self, data: dict, rules: list[dict]) -> dict:
        errors: list[ValidationError] = []
        parsed_rules = [ValidationRule(
            field=r["field"], rule_type=r["rule"],
            value=r.get("value", ""), message=r.get("message", ""),
        ) for r in rules]

        for rule in parsed_rules:
            value = data.get(rule.field)
            error = self._check_rule(rule, value)
            if error:
                errors.append(error)

        return {
            "valid": len(errors) == 0,
            "errors": [{"field": e.field, "message": e.message, "rule": e.rule}
                       for e in errors],
        }

    def _check_rule(self, rule: ValidationRule, value: object) -> ValidationError | None:
        msg = rule.message

        if rule.rule_type == "required":
            if value is None or value == "":
                return ValidationError(rule.field, msg or f"{rule.field} is required", "required")

        if value is None:
            return None  # skip other checks if value absent and not required

        if rule.rule_type == "type":
            expected = str(rule.value)
            type_map = {"string": str, "integer": int, "float": (int, float),
                        "boolean": bool, "list": list, "dict": dict}
            expected_type = type_map.get(expected)
            if expected_type and not isinstance(value, expected_type):
                return ValidationError(rule.field, msg or f"{rule.field} must be {expected}", "type")

        if rule.rule_type == "min" and isinstance(value, (int, float)):
            if value < float(rule.value):
                return ValidationError(rule.field, msg or f"{rule.field} must be >= {rule.value}", "min")

        if rule.rule_type == "max" and isinstance(value, (int, float)):
            if value > float(rule.value):
                return ValidationError(rule.field, msg or f"{rule.field} must be <= {rule.value}", "max")

        if rule.rule_type == "minlen" and isinstance(value, str):
            if len(value) < int(rule.value):
                return ValidationError(rule.field, msg or f"{rule.field} must be at least {rule.value} chars", "minlen")

        if rule.rule_type == "maxlen" and isinstance(value, str):
            if len(value) > int(rule.value):
                return ValidationError(rule.field, msg or f"{rule.field} must be at most {rule.value} chars", "maxlen")

        if rule.rule_type == "pattern" and isinstance(value, str):
            if not re.fullmatch(str(rule.value), value):
                return ValidationError(rule.field, msg or f"{rule.field} does not match pattern", "pattern")

        if rule.rule_type == "enum" and isinstance(rule.value, list):
            if value not in rule.value:
                return ValidationError(rule.field, msg or f"{rule.field} must be one of {rule.value}", "enum")

        return None

    def sanitize(self, data: dict) -> dict:
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                result[key] = self.sanitize(value)
            else:
                result[key] = value
        return result

    def _sanitize_string(self, value: str) -> str:
        sanitized = html.escape(value)
        for pattern in XSS_PATTERNS:
            if pattern.search(value):
                sanitized = pattern.sub("", sanitized)
        return sanitized.strip()

    def has_xss(self, value: str) -> bool:
        return any(p.search(value) for p in XSS_PATTERNS)

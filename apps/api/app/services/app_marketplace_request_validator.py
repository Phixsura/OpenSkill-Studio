"""Request Validator — validate and sanitize incoming API requests.

Provides schema-based request validation, input sanitization,
and structured error responses for the extension API layer.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    field: str
    message: str
    code: str


class RequestValidator:
    """Validates and sanitizes API request payloads."""

    MAX_STRING_LENGTH = 10000
    MAX_ARRAY_LENGTH = 1000

    SANITIZE_PATTERNS = [
        (re.compile(r'<script[^>]*>.*?</script>', re.I | re.S), ""),  # strip scripts
        (re.compile(r'javascript:', re.I), ""),  # strip JS URIs
        (re.compile(r'on\w+\s*=', re.I), ""),  # strip event handlers
    ]

    def validate_required(self, data: dict, fields: list[str]) -> list[ValidationError]:
        errors = []
        for f in fields:
            if f not in data or data[f] is None or (isinstance(data[f], str) and not data[f].strip()):
                errors.append(ValidationError(f, f"Field '{f}' is required", "required"))
        return errors

    def validate_types(self, data: dict, schema: dict[str, str]) -> list[ValidationError]:
        """Validate field types. Schema: {field: type_name}."""
        errors = []
        type_map = {"string": str, "int": int, "float": (int, float), "bool": bool,
                     "list": list, "dict": dict}
        for field_name, type_name in schema.items():
            if field_name not in data:
                continue
            expected = type_map.get(type_name)
            if expected and not isinstance(data[field_name], expected):
                errors.append(ValidationError(field_name,
                    f"Expected {type_name}, got {type(data[field_name]).__name__}", "type_error"))
        return errors

    def validate_length(self, data: dict, limits: dict[str, int]) -> list[ValidationError]:
        """Validate string/array lengths. limits: {field: max_length}."""
        errors = []
        for field_name, max_len in limits.items():
            value = data.get(field_name)
            if isinstance(value, (str, list)) and len(value) > max_len:
                errors.append(ValidationError(field_name,
                    f"Exceeds max length {max_len} (got {len(value)})", "max_length"))
        return errors

    def validate_pattern(self, data: dict, patterns: dict[str, str]) -> list[ValidationError]:
        """Validate string fields against regex patterns."""
        errors = []
        for field_name, pattern in patterns.items():
            value = data.get(field_name)
            if isinstance(value, str) and not re.match(pattern, value):
                errors.append(ValidationError(field_name,
                    f"Does not match required pattern", "pattern"))
        return errors

    def sanitize_string(self, value: str) -> str:
        """Sanitize a string by removing dangerous patterns."""
        result = value[:self.MAX_STRING_LENGTH]
        for pattern, replacement in self.SANITIZE_PATTERNS:
            result = pattern.sub(replacement, result)
        return result.strip()

    def sanitize_dict(self, data: dict) -> dict:
        """Recursively sanitize all string values in a dict."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                result[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.sanitize_string(v) if isinstance(v, str)
                    else self.sanitize_dict(v) if isinstance(v, dict)
                    else v
                    for v in value[:self.MAX_ARRAY_LENGTH]
                ]
            else:
                result[key] = value
        return result

    def validate(self, data: dict, required: list[str] | None = None,
                 types: dict[str, str] | None = None,
                 lengths: dict[str, int] | None = None,
                 patterns: dict[str, str] | None = None) -> tuple[bool, list[ValidationError]]:
        """Run all validations and return (valid, errors)."""
        errors: list[ValidationError] = []
        if required:
            errors.extend(self.validate_required(data, required))
        if types:
            errors.extend(self.validate_types(data, types))
        if lengths:
            errors.extend(self.validate_length(data, lengths))
        if patterns:
            errors.extend(self.validate_pattern(data, patterns))
        return len(errors) == 0, errors

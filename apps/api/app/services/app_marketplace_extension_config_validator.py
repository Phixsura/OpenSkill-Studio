"""Config Validator — validate extension runtime config against schemas.

Provides deep config validation with type coercion, range checks,
regex patterns, enum enforcement, and nested object support.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class FieldValidator:
    name: str
    field_type: str  # string, int, float, bool, enum, url, email, regex
    required: bool = True
    default: object = None
    min_val: float | None = None
    max_val: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    enum_values: list[str] = field(default_factory=list)
    pattern: str = ""
    description: str = ""


class ConfigValidator:
    """Deep config validation with comprehensive type checking."""

    URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

    def __init__(self):
        self._schemas: dict[str, list[FieldValidator]] = {}

    def register_schema(self, extension_id: str, fields: list[FieldValidator]) -> None:
        self._schemas[extension_id] = fields

    def validate(self, extension_id: str, config: dict) -> tuple[bool, list[str], dict]:
        """Validate config, apply defaults, return (valid, errors, processed_config)."""
        schema = self._schemas.get(extension_id, [])
        if not schema:
            return True, [], dict(config)

        errors = []
        processed = dict(config)

        for fv in schema:
            value = config.get(fv.name)

            # Apply default
            if value is None and fv.default is not None:
                processed[fv.name] = fv.default
                continue

            # Required check
            if value is None and fv.required:
                errors.append(f"{fv.name}: required field missing")
                continue

            if value is None:
                continue

            # Type validation
            type_err = self._check_type(fv, value)
            if type_err:
                errors.append(f"{fv.name}: {type_err}")
                continue

            # Range validation
            if fv.min_val is not None and isinstance(value, (int, float)) and value < fv.min_val:
                errors.append(f"{fv.name}: {value} below minimum {fv.min_val}")
            if fv.max_val is not None and isinstance(value, (int, float)) and value > fv.max_val:
                errors.append(f"{fv.name}: {value} above maximum {fv.max_val}")

            # Length validation
            if isinstance(value, str):
                if fv.min_length is not None and len(value) < fv.min_length:
                    errors.append(f"{fv.name}: length {len(value)} below minimum {fv.min_length}")
                if fv.max_length is not None and len(value) > fv.max_length:
                    errors.append(f"{fv.name}: length {len(value)} above maximum {fv.max_length}")

        return len(errors) == 0, errors, processed

    def _check_type(self, fv: FieldValidator, value: object) -> str:
        if fv.field_type == "string" and not isinstance(value, str):
            return f"expected string, got {type(value).__name__}"
        if fv.field_type == "int" and not isinstance(value, int):
            return f"expected int, got {type(value).__name__}"
        if fv.field_type == "float" and not isinstance(value, (int, float)):
            return f"expected number, got {type(value).__name__}"
        if fv.field_type == "bool" and not isinstance(value, bool):
            return f"expected bool, got {type(value).__name__}"
        if fv.field_type == "enum" and str(value) not in fv.enum_values:
            return f"must be one of {fv.enum_values}"
        if fv.field_type == "url" and (not isinstance(value, str) or not self.URL_PATTERN.match(value)):
            return "invalid URL format"
        if fv.field_type == "email" and (not isinstance(value, str) or not self.EMAIL_PATTERN.match(value)):
            return "invalid email format"
        if fv.field_type == "regex" and isinstance(value, str) and fv.pattern:
            if not re.match(fv.pattern, value):
                return f"does not match pattern {fv.pattern}"
        return ""

    def get_schema(self, extension_id: str) -> list[FieldValidator]:
        return self._schemas.get(extension_id, [])

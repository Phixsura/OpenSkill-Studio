"""Config Schema Validator — validate app installation config against manifest-declared schemas.

Validates tenant-specific configuration values for installed apps:
- Type validation (string, integer, boolean, enum, url, email, json)
- Required/optional field enforcement
- Default value injection for missing optional fields
- Range constraints (min/max for numbers, minLength/maxLength for strings)
- Pattern matching (regex) for strings
- Enum value validation
- Nested object validation
- Sensitive field masking for display
- Config diff detection for upgrade migrations
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse

import structlog

log = structlog.get_logger()


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"
    URL = "url"
    EMAIL = "email"
    JSON = "json"
    OBJECT = "object"


@dataclass
class FieldSchema:
    """Schema definition for a single config field."""

    name: str
    field_type: FieldType
    required: bool = True
    default: object = None
    description: str = ""
    sensitive: bool = False  # mask in logs/display
    # Constraints
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None  # regex
    enum_values: list[str] | None = None  # for FieldType.ENUM
    # Nested object schema
    properties: dict[str, FieldSchema] | None = None  # for FieldType.OBJECT


@dataclass
class ValidationError:
    """A single config validation error."""

    field: str
    message: str
    value: object = None  # the invalid value (masked if sensitive)


@dataclass
class ValidationResult:
    """Result of validating a config object."""

    valid: bool
    errors: list[ValidationError]
    sanitized: dict  # config with defaults injected, sensitive values masked
    warnings: list[str]


@dataclass
class ConfigDiff:
    """Differences between two config versions."""

    added: list[str]     # fields in new but not old
    removed: list[str]   # fields in old but not new
    changed: list[str]   # fields with different values
    unchanged: list[str] # fields with same values


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class ConfigSchemaValidator:
    """Validate config values against a declared schema."""

    def __init__(self, schema: list[FieldSchema]):
        self._schema = {f.name: f for f in schema}

    @property
    def field_names(self) -> list[str]:
        return sorted(self._schema.keys())

    def validate(self, config: dict) -> ValidationResult:
        """Validate a config dict against the schema.

        Returns a ValidationResult with errors and a sanitized config
        (defaults injected, sensitive values masked for display).
        """
        errors: list[ValidationError] = []
        warnings: list[str] = []
        sanitized: dict = {}

        # Check required fields and validate present fields
        for name, field_schema in self._schema.items():
            value = config.get(name)

            if value is None:
                if field_schema.required:
                    if field_schema.default is not None:
                        sanitized[name] = field_schema.default
                    else:
                        errors.append(ValidationError(
                            field=name,
                            message=f"Required field '{name}' is missing",
                        ))
                else:
                    if field_schema.default is not None:
                        sanitized[name] = field_schema.default
                continue

            # Validate value
            field_errors = self._validate_field(name, value, field_schema)
            errors.extend(field_errors)

            # Sanitize for display
            if field_schema.sensitive:
                sanitized[name] = "••••••••"
            else:
                sanitized[name] = value

        # Check for unknown fields
        for key in config:
            if key not in self._schema:
                warnings.append(f"Unknown config field '{key}' — will be ignored")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            sanitized=sanitized,
            warnings=warnings,
        )

    def apply_defaults(self, config: dict) -> dict:
        """Return a new config with default values injected for missing optional fields."""
        result = dict(config)
        for name, field_schema in self._schema.items():
            if name not in result and field_schema.default is not None:
                result[name] = field_schema.default
        return result

    def diff(self, old_config: dict, new_config: dict) -> ConfigDiff:
        """Compute differences between two config versions."""
        old_keys = set(old_config.keys())
        new_keys = set(new_config.keys())
        all_keys = old_keys | new_keys

        added = sorted(new_keys - old_keys)
        removed = sorted(old_keys - new_keys)
        changed = []
        unchanged = []

        for key in sorted(old_keys & new_keys):
            if old_config[key] != new_config[key]:
                changed.append(key)
            else:
                unchanged.append(key)

        return ConfigDiff(added=added, removed=removed, changed=changed, unchanged=unchanged)

    def mask_sensitive(self, config: dict) -> dict:
        """Return a copy with sensitive fields masked."""
        result = dict(config)
        for name, field_schema in self._schema.items():
            if field_schema.sensitive and name in result:
                result[name] = "••••••••"
        return result

    # ── Internal validation ──────────────────────────────

    def _validate_field(self, name: str, value: object,
                        schema: FieldSchema) -> list[ValidationError]:
        errors: list[ValidationError] = []
        display_value = "••••••••" if schema.sensitive else value

        # Type validation
        type_valid = self._check_type(value, schema.field_type)
        if not type_valid:
            errors.append(ValidationError(
                field=name,
                message=f"Expected {schema.field_type.value}, got {type(value).__name__}",
                value=display_value,
            ))
            return errors  # Skip further checks if type is wrong

        # String constraints
        if isinstance(value, str):
            if schema.min_length is not None and len(value) < schema.min_length:
                errors.append(ValidationError(
                    field=name,
                    message=f"Must be at least {schema.min_length} characters",
                    value=display_value,
                ))
            if schema.max_length is not None and len(value) > schema.max_length:
                errors.append(ValidationError(
                    field=name,
                    message=f"Must be at most {schema.max_length} characters",
                    value=display_value,
                ))
            if schema.pattern:
                if not re.match(schema.pattern, value):
                    errors.append(ValidationError(
                        field=name,
                        message=f"Does not match pattern: {schema.pattern}",
                        value=display_value,
                    ))

        # Number constraints
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if schema.min_value is not None and value < schema.min_value:
                errors.append(ValidationError(
                    field=name,
                    message=f"Must be >= {schema.min_value}",
                    value=display_value,
                ))
            if schema.max_value is not None and value > schema.max_value:
                errors.append(ValidationError(
                    field=name,
                    message=f"Must be <= {schema.max_value}",
                    value=display_value,
                ))

        # Enum validation
        if schema.field_type == FieldType.ENUM and schema.enum_values:
            if value not in schema.enum_values:
                errors.append(ValidationError(
                    field=name,
                    message=f"Must be one of: {', '.join(schema.enum_values)}",
                    value=display_value,
                ))

        # URL validation
        if schema.field_type == FieldType.URL and isinstance(value, str):
            try:
                parsed = urlparse(value)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError
            except Exception:
                errors.append(ValidationError(
                    field=name, message="Invalid URL format", value=display_value,
                ))

        # Email validation
        if schema.field_type == FieldType.EMAIL and isinstance(value, str):
            if not EMAIL_RE.match(value):
                errors.append(ValidationError(
                    field=name, message="Invalid email format", value=display_value,
                ))

        # Nested object
        if schema.field_type == FieldType.OBJECT and schema.properties:
            if isinstance(value, dict):
                for prop_name, prop_schema in schema.properties.items():
                    prop_value = value.get(prop_name)
                    if prop_value is None and prop_schema.required:
                        errors.append(ValidationError(
                            field=f"{name}.{prop_name}",
                            message=f"Required nested field '{prop_name}' is missing",
                        ))
                    elif prop_value is not None:
                        nested_errors = self._validate_field(
                            f"{name}.{prop_name}", prop_value, prop_schema
                        )
                        errors.extend(nested_errors)

        return errors

    @staticmethod
    def _check_type(value: object, field_type: FieldType) -> bool:
        if field_type == FieldType.STRING:
            return isinstance(value, str)
        elif field_type == FieldType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)
        elif field_type == FieldType.NUMBER:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif field_type == FieldType.BOOLEAN:
            return isinstance(value, bool)
        elif field_type == FieldType.ENUM:
            return isinstance(value, str)
        elif field_type == FieldType.URL:
            return isinstance(value, str)
        elif field_type == FieldType.EMAIL:
            return isinstance(value, str)
        elif field_type == FieldType.JSON:
            return isinstance(value, (dict, list))
        elif field_type == FieldType.OBJECT:
            return isinstance(value, dict)
        return True

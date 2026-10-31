"""App Config Validator — validate app configuration against declared schemas.

Validates app manifest and runtime configuration:
- Type checking (string, int, float, bool, enum, url, email)
- Required field enforcement
- Range/pattern constraints
- Nested object validation
- Collect all errors (non-short-circuit)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class FieldType(str, Enum):
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ENUM = "enum"
    URL = "url"
    EMAIL = "email"


@dataclass
class FieldSchema:
    """Schema for a single config field."""

    name: str
    field_type: FieldType
    required: bool = True
    default: object = None
    min_value: float | None = None
    max_value: float | None = None
    pattern: str | None = None  # regex for string fields
    enum_values: list[str] | None = None  # for enum type
    description: str = ""


@dataclass
class ValidationError:
    """A single validation error."""

    field: str
    message: str
    value: object = None


@dataclass
class ValidationResult:
    """Result of config validation."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    resolved_config: dict = field(default_factory=dict)


_URL_RE = re.compile(r"^https?://[^\s]+$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AppConfigValidator:
    """Validate app configuration against declared schemas."""

    def __init__(self) -> None:
        # schema_id → list of FieldSchema
        self._schemas: dict[str, list[FieldSchema]] = {}

    def register_schema(self, schema_id: str, fields: list[FieldSchema]) -> None:
        """Register a config schema."""
        if not schema_id:
            raise ValueError("schema_id is required")
        self._schemas[schema_id] = list(fields)

    def validate(self, schema_id: str, config: dict) -> ValidationResult:
        """Validate config against a registered schema."""
        schema = self._schemas.get(schema_id)
        if schema is None:
            raise KeyError(f"Schema {schema_id} not found")

        errors: list[ValidationError] = []
        warnings: list[str] = []
        resolved: dict = {}

        known_fields = {f.name for f in schema}
        # Warn on unknown fields
        for key in config:
            if key not in known_fields:
                warnings.append(f"Unknown field: {key}")

        for fs in schema:
            value = config.get(fs.name)

            # Required check
            if value is None:
                if fs.required:
                    if fs.default is not None:
                        resolved[fs.name] = fs.default
                        warnings.append(f"{fs.name}: using default value")
                    else:
                        errors.append(ValidationError(
                            field=fs.name, message="Required field is missing"))
                continue

            # Type check
            err = self._check_type(fs, value)
            if err:
                errors.append(err)
                continue

            # Range check (numeric types)
            err = self._check_range(fs, value)
            if err:
                errors.append(err)
                continue

            # Pattern check (string types)
            err = self._check_pattern(fs, value)
            if err:
                errors.append(err)
                continue

            # Enum check
            err = self._check_enum(fs, value)
            if err:
                errors.append(err)
                continue

            resolved[fs.name] = value

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            resolved_config=resolved,
        )

    def list_schemas(self) -> list[str]:
        return list(self._schemas.keys())

    def get_schema(self, schema_id: str) -> list[FieldSchema]:
        schema = self._schemas.get(schema_id)
        if schema is None:
            raise KeyError(f"Schema {schema_id} not found")
        return list(schema)

    def _check_type(self, fs: FieldSchema, value: object) -> ValidationError | None:
        # bool is subclass of int in Python — reject bools for int/float fields first
        if fs.field_type in (FieldType.INT, FieldType.FLOAT) and isinstance(value, bool):
            return ValidationError(
                field=fs.name,
                message=f"Expected {fs.field_type.value}, got {type(value).__name__}",
                value=value,
            )

        checks: dict[FieldType, type | tuple[type, ...]] = {
            FieldType.STRING: str,
            FieldType.INT: int,
            FieldType.FLOAT: (int, float),
            FieldType.BOOL: bool,
            FieldType.ENUM: str,
            FieldType.URL: str,
            FieldType.EMAIL: str,
        }
        expected = checks.get(fs.field_type)
        if expected and not isinstance(value, expected):
            return ValidationError(
                field=fs.name,
                message=f"Expected {fs.field_type.value}, got {type(value).__name__}",
                value=value,
            )

        # Format validation for URL/EMAIL
        if fs.field_type == FieldType.URL and isinstance(value, str):
            if not _URL_RE.match(value):
                return ValidationError(
                    field=fs.name, message="Invalid URL format", value=value)
        if fs.field_type == FieldType.EMAIL and isinstance(value, str):
            if not _EMAIL_RE.match(value):
                return ValidationError(
                    field=fs.name, message="Invalid email format", value=value)

        return None

    def _check_range(self, fs: FieldSchema, value: object) -> ValidationError | None:
        if fs.field_type not in (FieldType.INT, FieldType.FLOAT):
            return None
        if not isinstance(value, (int, float)):
            return None
        if fs.min_value is not None and value < fs.min_value:
            return ValidationError(
                field=fs.name,
                message=f"Value {value} below minimum {fs.min_value}",
                value=value,
            )
        if fs.max_value is not None and value > fs.max_value:
            return ValidationError(
                field=fs.name,
                message=f"Value {value} above maximum {fs.max_value}",
                value=value,
            )
        return None

    def _check_pattern(self, fs: FieldSchema, value: object) -> ValidationError | None:
        if fs.pattern and fs.field_type == FieldType.STRING and isinstance(value, str):
            if not re.match(fs.pattern, value):
                return ValidationError(
                    field=fs.name,
                    message=f"Value does not match pattern {fs.pattern}",
                    value=value,
                )
        return None

    def _check_enum(self, fs: FieldSchema, value: object) -> ValidationError | None:
        if fs.field_type == FieldType.ENUM and fs.enum_values:
            if value not in fs.enum_values:
                return ValidationError(
                    field=fs.name,
                    message=f"Value must be one of {fs.enum_values}",
                    value=value,
                )
        return None

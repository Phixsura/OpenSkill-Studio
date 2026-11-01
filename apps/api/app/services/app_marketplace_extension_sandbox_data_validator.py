"""Sandbox Data Validator — schema-driven data validation for sandbox I/O.

Validates structured data with nested schemas, custom rules, batch
validation, and detailed error paths for nested objects.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FieldSchema:
    name: str
    field_type: str  # string, integer, float, boolean, array, object
    required: bool = True
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str = ""
    enum_values: list | None = None
    items_type: str = ""  # for arrays
    nested: list["FieldSchema"] | None = None  # for objects


@dataclass
class ValidationError:
    path: str
    message: str
    value: object = None


TYPE_MAP = {
    "string": str, "integer": int, "float": (int, float),
    "boolean": bool, "array": list, "object": dict,
}


class SandboxDataValidatorService:
    """Schema-driven data validation with nested path support."""

    def validate(self, data: dict, schema: list[dict]) -> dict:
        parsed = [self._parse_field(f) for f in schema]
        errors: list[ValidationError] = []
        self._validate_fields(data, parsed, "", errors)
        return {
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "errors": [{"path": e.path, "message": e.message} for e in errors],
        }

    def _parse_field(self, f: dict) -> FieldSchema:
        nested = [self._parse_field(n) for n in f.get("nested", [])] if f.get("nested") else None
        return FieldSchema(
            name=f["name"], field_type=f["type"],
            required=f.get("required", True),
            min_value=f.get("min"), max_value=f.get("max"),
            min_length=f.get("min_length"), max_length=f.get("max_length"),
            pattern=f.get("pattern", ""), enum_values=f.get("enum"),
            items_type=f.get("items_type", ""), nested=nested,
        )

    def _validate_fields(self, data: dict, fields: list[FieldSchema],
                         prefix: str, errors: list[ValidationError]) -> None:
        for field in fields:
            path = f"{prefix}.{field.name}" if prefix else field.name
            value = data.get(field.name)

            if value is None:
                if field.required:
                    errors.append(ValidationError(path, f"Required field missing"))
                continue

            # Type check
            expected = TYPE_MAP.get(field.field_type)
            if expected and not isinstance(value, expected):
                if field.field_type == "float" and isinstance(value, bool):
                    errors.append(ValidationError(path, f"Expected {field.field_type}"))
                    continue
                if field.field_type == "integer" and isinstance(value, bool):
                    errors.append(ValidationError(path, f"Expected integer"))
                    continue
                errors.append(ValidationError(path, f"Expected {field.field_type}, got {type(value).__name__}"))
                continue

            # Numeric constraints
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if field.min_value is not None and value < field.min_value:
                    errors.append(ValidationError(path, f"Must be >= {field.min_value}"))
                if field.max_value is not None and value > field.max_value:
                    errors.append(ValidationError(path, f"Must be <= {field.max_value}"))

            # String constraints
            if isinstance(value, str):
                if field.min_length is not None and len(value) < field.min_length:
                    errors.append(ValidationError(path, f"Min length {field.min_length}"))
                if field.max_length is not None and len(value) > field.max_length:
                    errors.append(ValidationError(path, f"Max length {field.max_length}"))

            # Enum check
            if field.enum_values and value not in field.enum_values:
                errors.append(ValidationError(path, f"Must be one of {field.enum_values}"))

            # Nested object validation
            if field.field_type == "object" and field.nested and isinstance(value, dict):
                self._validate_fields(value, field.nested, path, errors)

            # Array item type check
            if field.field_type == "array" and field.items_type and isinstance(value, list):
                item_expected = TYPE_MAP.get(field.items_type)
                for i, item in enumerate(value):
                    if item_expected and not isinstance(item, item_expected):
                        errors.append(ValidationError(
                            f"{path}[{i}]", f"Expected {field.items_type}"))

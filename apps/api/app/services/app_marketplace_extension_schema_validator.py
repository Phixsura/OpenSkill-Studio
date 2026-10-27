"""Schema Validator — validate data against JSON Schema-like definitions.

Implements:
- Type checking (string, integer, number, boolean, array, object, null)
- Required fields, min/max length, min/max value
- Pattern matching via regex
- Nested object and array item validation
- Custom error messages with field paths
"""
from __future__ import annotations
import re


class SchemaValidationError:
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
    def __repr__(self):
        return f"{self.path}: {self.message}"


class SchemaValidatorService:
    TYPE_MAP = {
        "string": str, "integer": int, "number": (int, float),
        "boolean": bool, "array": list, "object": dict,
    }

    def validate(self, data: object, schema: dict, path: str = "") -> list[SchemaValidationError]:
        errors: list[SchemaValidationError] = []
        expected_type = schema.get("type")

        # Null check
        if data is None:
            if schema.get("nullable"):
                return errors
            if expected_type:
                errors.append(SchemaValidationError(path or "$", f"Expected {expected_type}, got null"))
            return errors

        # Type check
        if expected_type and expected_type != "null":
            py_type = self.TYPE_MAP.get(expected_type)
            if py_type and not isinstance(data, py_type):
                # Special case: bool is int in Python
                if expected_type == "integer" and isinstance(data, bool):
                    errors.append(SchemaValidationError(path or "$", f"Expected integer, got boolean"))
                    return errors
                errors.append(SchemaValidationError(path or "$", f"Expected {expected_type}, got {type(data).__name__}"))
                return errors

        # String validations
        if isinstance(data, str):
            min_len = schema.get("minLength")
            max_len = schema.get("maxLength")
            pattern = schema.get("pattern")
            if min_len is not None and len(data) < min_len:
                errors.append(SchemaValidationError(path or "$", f"Length {len(data)} < minLength {min_len}"))
            if max_len is not None and len(data) > max_len:
                errors.append(SchemaValidationError(path or "$", f"Length {len(data)} > maxLength {max_len}"))
            if pattern and not re.search(pattern, data):
                errors.append(SchemaValidationError(path or "$", f"Does not match pattern: {pattern}"))
            enum = schema.get("enum")
            if enum and data not in enum:
                errors.append(SchemaValidationError(path or "$", f"Must be one of: {enum}"))

        # Number validations
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")
            if minimum is not None and data < minimum:
                errors.append(SchemaValidationError(path or "$", f"Value {data} < minimum {minimum}"))
            if maximum is not None and data > maximum:
                errors.append(SchemaValidationError(path or "$", f"Value {data} > maximum {maximum}"))

        # Object validations
        if isinstance(data, dict):
            properties = schema.get("properties", {})
            required = set(schema.get("required", []))
            additional = schema.get("additionalProperties", True)

            for field_name in required:
                if field_name not in data:
                    fp = f"{path}.{field_name}" if path else field_name
                    errors.append(SchemaValidationError(fp, "Required field missing"))

            for field_name, value in data.items():
                fp = f"{path}.{field_name}" if path else field_name
                if field_name in properties:
                    errors.extend(self.validate(value, properties[field_name], fp))
                elif not additional:
                    errors.append(SchemaValidationError(fp, "Additional property not allowed"))

        # Array validations
        if isinstance(data, list):
            min_items = schema.get("minItems")
            max_items = schema.get("maxItems")
            items_schema = schema.get("items")
            if min_items is not None and len(data) < min_items:
                errors.append(SchemaValidationError(path or "$", f"Array length {len(data)} < minItems {min_items}"))
            if max_items is not None and len(data) > max_items:
                errors.append(SchemaValidationError(path or "$", f"Array length {len(data)} > maxItems {max_items}"))
            if items_schema:
                for i, item in enumerate(data):
                    errors.extend(self.validate(item, items_schema, f"{path}[{i}]"))

        return errors

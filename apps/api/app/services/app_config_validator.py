"""App config validator — validates installation config against manifest config_schema.

Uses JSON Schema-like validation without requiring jsonschema library,
keeping the dependency footprint minimal.
"""

import re
import structlog

log = structlog.get_logger()


def validate_config(config: dict, schema: dict) -> list[str]:
    """Validate an installation config dict against a manifest config_schema.

    Returns a list of error messages (empty = valid).
    """
    errors: list[str] = []

    if not isinstance(config, dict):
        return ["Config must be an object"]

    if not isinstance(schema, dict):
        return []  # No schema = no validation

    schema_type = schema.get("type")
    if schema_type and schema_type != "object":
        errors.append(f"Config schema type must be 'object', got '{schema_type}'")
        return errors

    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # Check required fields
    for field in required:
        if field not in config:
            errors.append(f"Missing required config field: {field}")

    # Check property types
    for field, prop_schema in properties.items():
        if field not in config:
            continue

        value = config[field]
        expected_type = prop_schema.get("type")

        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"Config field '{field}' must be a string")
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append(f"Config field '{field}' must be an integer")
        elif expected_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"Config field '{field}' must be a number")
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append(f"Config field '{field}' must be a boolean")
        elif expected_type == "array" and not isinstance(value, list):
            errors.append(f"Config field '{field}' must be an array")

        # String constraints
        if expected_type == "string" and isinstance(value, str):
            min_len = prop_schema.get("minLength")
            max_len = prop_schema.get("maxLength")
            pattern = prop_schema.get("pattern")
            if min_len and len(value) < min_len:
                errors.append(f"Config field '{field}' must be at least {min_len} chars")
            if max_len and len(value) > max_len:
                errors.append(f"Config field '{field}' must be at most {max_len} chars")
            if pattern and not re.match(pattern, value):
                errors.append(f"Config field '{field}' does not match pattern")

        # Enum constraint
        enum_values = prop_schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"Config field '{field}' must be one of: {', '.join(str(v) for v in enum_values)}")

    # Check for unknown fields (if additionalProperties is false)
    if schema.get("additionalProperties") is False:
        unknown = set(config.keys()) - set(properties.keys())
        for field in unknown:
            errors.append(f"Unknown config field: {field}")

    return errors

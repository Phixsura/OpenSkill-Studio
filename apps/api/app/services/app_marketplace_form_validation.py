"""Form validation — reusable validation rules for marketplace forms."""

import re

VALIDATORS = {
    "required": lambda v: bool(v) if isinstance(v, str) else v is not None,
    "email": lambda v: bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', str(v))),
    "url": lambda v: bool(re.match(r'^https?://.+', str(v))),
    "slug": lambda v: bool(re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', str(v))),
    "min_length_3": lambda v: len(str(v)) >= 3,
    "min_length_5": lambda v: len(str(v)) >= 5,
    "max_length_50": lambda v: len(str(v)) <= 50,
    "max_length_200": lambda v: len(str(v)) <= 200,
}


def validate_field(*, value: object, rules: list[str]) -> dict:
    errors = []
    for rule in rules:
        validator = VALIDATORS.get(rule)
        if validator and not validator(value):
            errors.append(rule)
    return {"valid": len(errors) == 0, "errors": errors}


def validate_form(*, fields: dict[str, object], schema: dict[str, list[str]]) -> dict:
    results = {}
    all_valid = True
    for field_name, rules in schema.items():
        value = fields.get(field_name)
        result = validate_field(value=value, rules=rules)
        results[field_name] = result
        if not result["valid"]:
            all_valid = False
    return {"valid": all_valid, "fields": results,
            "error_count": sum(len(r["errors"]) for r in results.values())}

"""Form validator — declarative field validation engine."""

import re
import html

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
URL_RE = re.compile(r"^https?://[^\s]+$")


def validate_field(*, value: str, rules: list[dict]) -> dict:
    errors = []
    for rule in rules:
        t = rule["type"]
        if t == "required" and not value.strip():
            errors.append(rule.get("message", "This field is required"))
        elif t == "min_length" and len(value) < rule.get("min", 0):
            errors.append(rule.get("message", f"Minimum {rule['min']} characters"))
        elif t == "max_length" and len(value) > rule.get("max", 9999):
            errors.append(rule.get("message", f"Maximum {rule['max']} characters"))
        elif t == "email" and value and not EMAIL_RE.match(value):
            errors.append(rule.get("message", "Invalid email address"))
        elif t == "url" and value and not URL_RE.match(value):
            errors.append(rule.get("message", "Invalid URL"))
        elif t == "pattern" and value and not re.match(rule.get("pattern", ""), value):
            errors.append(rule.get("message", "Invalid format"))
    return {"valid": len(errors) == 0, "errors": errors, "value": html.escape(value)}


def validate_form(*, fields: dict[str, str], schema: dict[str, list[dict]]) -> dict:
    results = {}
    all_valid = True
    for name, rules in schema.items():
        r = validate_field(value=fields.get(name, ""), rules=rules)
        results[name] = r
        if not r["valid"]:
            all_valid = False
    return {"valid": all_valid, "fields": results,
            "error_count": sum(len(r["errors"]) for r in results.values())}

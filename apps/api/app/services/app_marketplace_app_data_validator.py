"""Data validator — validate common data formats."""

import re

VALIDATORS = {
    "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
    "url": re.compile(r"^https?://[^\s]+$"),
    "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I),
    "semver": re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$"),
    "slug": re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$"),
    "hex_color": re.compile(r"^#[0-9a-fA-F]{6}$"),
    "ipv4": re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
}


def validate(*, value: str, format_type: str) -> dict:
    pattern = VALIDATORS.get(format_type)
    if not pattern:
        return {"valid": False, "error": f"Unknown format. Valid: {', '.join(sorted(VALIDATORS))}"}
    matched = bool(pattern.match(value))
    return {"valid": matched, "value": value, "format": format_type,
            "error": None if matched else f"Does not match {format_type} format"}


def validate_batch(*, items: list[dict]) -> dict:
    results = []
    for item in items:
        r = validate(value=item["value"], format_type=item["format"])
        results.append({**r, "field": item.get("field", "")})
    valid_count = sum(1 for r in results if r["valid"])
    return {"results": results, "total": len(results), "valid_count": valid_count,
            "all_valid": valid_count == len(results)}

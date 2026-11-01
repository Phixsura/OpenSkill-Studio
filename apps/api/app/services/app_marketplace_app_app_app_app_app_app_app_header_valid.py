"""Request header validator — validate required and forbidden headers."""
from __future__ import annotations


def validate_headers(headers: dict[str, str], rules: dict) -> dict:
    errors = []
    for h in rules.get("required", []):
        if h.lower() not in {k.lower() for k in headers}:
            errors.append({"header": h, "error": "missing_required"})
    for h in rules.get("forbidden", []):
        if h.lower() in {k.lower() for k in headers}:
            errors.append({"header": h, "error": "forbidden_header"})
    max_size = rules.get("max_size_bytes", 8192)
    total_size = sum(len(k) + len(v) for k, v in headers.items())
    if total_size > max_size:
        errors.append({"header": "total", "error": f"headers_too_large ({total_size} > {max_size})"})
    return {"valid": len(errors) == 0, "errors": errors, "headers_checked": len(headers),
            "total_size_bytes": total_size}

"""R487: bounded canonical-model schema validation (Airbyte discover parity).

The catalog (MODEL_SCHEMAS) is a deliberately small JSON-Schema subset —
`type`, `format` (email/date/date-time), `enum`, `maxLength` on properties —
validated by this hand-rolled walker rather than a jsonschema dependency:
the subset is tiny, the walker is total over untrusted payloads (R87
lesson), and nothing here is extensible by user input.

Used by the opt-in strict_schema gate (sync engine) AFTER the required-key
check; errors become schema_invalid conflicts, never staged junk. Unknown
keys always pass (mappings may carry extras; provisioning ignores them).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.integrations.models.sync import MODEL_SCHEMAS

_TYPE_CHECKS: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
    "array": list,
    "object": dict,
}


def _format_ok(fmt: str, value: str) -> bool:
    if fmt == "email":
        # Same looseness as the SCIM/roster boundary: one @, non-empty halves.
        parts = value.split("@")
        return len(parts) == 2 and bool(parts[0]) and bool(parts[1])
    try:
        if fmt == "date":
            date.fromisoformat(value[:10])
        elif fmt == "date-time":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return False
    return True


def validate_model_payload(model: str, payload: Any) -> list[str]:
    """Return a bounded list of human-readable violations ([] = valid).

    Only keys PRESENT in the payload and DECLARED in the schema are checked
    (required-ness is the separate MODEL_REQUIRED_KEYS gate). None values
    pass: optionality is uniform, absence and null are equivalent here.
    """
    schema = MODEL_SCHEMAS.get(model)
    if schema is None:
        return []
    if not isinstance(payload, dict):
        return ["payload is not an object"]
    errors: list[str] = []
    for key, spec in schema.get("properties", {}).items():
        if key not in payload or payload[key] is None:
            continue
        value = payload[key]
        expected = spec.get("type")
        check = _TYPE_CHECKS.get(expected or "")
        if check is not None and not isinstance(value, check):
            errors.append(f"{key}: expected {expected}")
            continue
        # bool is an int subclass — reject True where integer/number expected.
        if expected in ("integer", "number") and isinstance(value, bool):
            errors.append(f"{key}: expected {expected}")
            continue
        if isinstance(value, str):
            max_len = spec.get("maxLength")
            if max_len is not None and len(value) > max_len:
                errors.append(f"{key}: longer than {max_len}")
                continue
            fmt = spec.get("format")
            if fmt and not _format_ok(fmt, value):
                errors.append(f"{key}: bad {fmt}")
                continue
        enum = spec.get("enum")
        if enum is not None and value not in enum:
            errors.append(f"{key}: not in enum")
        if len(errors) >= 10:  # bounded detail, matching the mapping gate
            break
    return errors

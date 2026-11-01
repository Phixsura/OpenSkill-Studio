"""Env var editor — manage environment variables with masking."""

import html
import re

KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")
SENSITIVE_PATTERNS = {"PASSWORD", "SECRET", "TOKEN", "KEY", "API_KEY", "PRIVATE"}


def validate_env_var(*, key: str, value: str) -> dict:
    errors = []
    if not KEY_RE.match(key):
        errors.append("Key must be uppercase letters, digits, underscores; start with letter; max 128 chars")
    if len(value) > 32768:
        errors.append("Value too long (max 32KB)")
    is_sensitive = any(p in key.upper() for p in SENSITIVE_PATTERNS)
    return {"valid": len(errors) == 0, "errors": errors,
            "is_sensitive": is_sensitive, "key": key}


def build_env_list(*, variables: list[dict]) -> dict:
    items = []
    for v in variables:
        key = v["key"]
        val = v.get("value", "")
        is_sensitive = any(p in key.upper() for p in SENSITIVE_PATTERNS)
        masked = val[:2] + "•" * min(len(val) - 2, 20) if is_sensitive and len(val) > 2 else val
        items.append({"key": html.escape(key), "value": html.escape(masked),
                       "is_sensitive": is_sensitive, "source": v.get("source", "manual")})
    return {"variables": items, "total": len(items),
            "sensitive_count": sum(1 for i in items if i["is_sensitive"])}

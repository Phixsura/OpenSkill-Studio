"""Sandbox environment validator — validate env vars before injection."""

import re

_SAFE_VALUE_RE = re.compile(r"^[\x20-\x7E]{0,10000}$")  # printable ASCII only
_SAFE_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")

FORBIDDEN_ENV_PREFIXES = ("PATH", "HOME", "USER", "SHELL", "LD_", "DYLD_", "PYTHONPATH", "NODE_PATH")


def validate_env_var(key: str, value: str) -> list[str]:
    """Validate a single env var for sandbox injection."""
    errors = []
    if not _SAFE_KEY_RE.match(key):
        errors.append(f"Key '{key}' must be UPPER_SNAKE_CASE, 1-128 chars")
    if any(key.startswith(p) for p in FORBIDDEN_ENV_PREFIXES):
        errors.append(f"Key '{key}' uses a forbidden prefix")
    if not _SAFE_VALUE_RE.match(value):
        errors.append(f"Value for '{key}' contains invalid characters or is too long")
    return errors


def validate_env_map(env: dict[str, str]) -> list[str]:
    """Validate all env vars in a map."""
    errors = []
    for k, v in env.items():
        errors.extend(validate_env_var(k, str(v)))
    return errors

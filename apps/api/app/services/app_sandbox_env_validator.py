"""Sandbox environment validator — allowlist-based env var validation.

Only keys matching OPENSKILL_ or APP_ prefixes are allowed.
This prevents injection of dangerous env vars like LD_PRELOAD, PATH, etc.
"""

import re

_ALLOWED_KEY_RE = re.compile(r"^(OPENSKILL_|APP_)[A-Z0-9_]{1,120}$")
_SAFE_VALUE_RE = re.compile(r"^[\x20-\x7E]{0,10000}$")  # printable ASCII only


def validate_env_var(key: str, value: str) -> list[str]:
    """Validate a single env var — allowlist approach."""
    errors = []
    if not _ALLOWED_KEY_RE.match(key):
        errors.append(f"Key '{key}' must start with OPENSKILL_ or APP_ and be UPPER_SNAKE_CASE")
    if not _SAFE_VALUE_RE.match(value):
        errors.append(f"Value for '{key}' contains invalid characters or is too long")
    return errors


def validate_env_map(env: dict[str, str]) -> list[str]:
    """Validate all env vars in a map."""
    errors = []
    for k, v in env.items():
        errors.extend(validate_env_var(k, str(v)))
    return errors

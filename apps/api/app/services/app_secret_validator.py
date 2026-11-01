"""Secret validator — validate secret key names and values."""

import re

KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
FORBIDDEN_KEYS = frozenset({"PASSWORD", "PASSWD", "SECRET", "TOKEN", "KEY"})  # Too generic
MAX_VALUE_LENGTH = 10_000


def validate_secret_key(key: str) -> list[str]:
    """Validate a secret key name."""
    errors = []
    if not key:
        errors.append("Key is required")
    elif not KEY_PATTERN.match(key):
        errors.append("Key must be UPPER_SNAKE_CASE, 2-64 chars, starting with letter")
    if key in FORBIDDEN_KEYS:
        errors.append(f"Key '{key}' is too generic — use a more descriptive name")
    return errors


def validate_secret_value(value: str) -> list[str]:
    """Validate a secret value."""
    errors = []
    if not value:
        errors.append("Value is required")
    elif len(value) > MAX_VALUE_LENGTH:
        errors.append(f"Value too long ({len(value)} chars, max {MAX_VALUE_LENGTH})")
    return errors

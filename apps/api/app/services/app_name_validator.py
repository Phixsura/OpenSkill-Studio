"""App name validator — validate app display names."""

import re

MIN_LENGTH = 2
MAX_LENGTH = 100
RESERVED_NAMES = frozenset({"OpenSkill", "Admin", "System", "Platform", "Test App", "Example"})
PROFANITY_PATTERNS = [re.compile(r"fuck|shit|damn|ass\b", re.I)]


def validate_app_name(name: str) -> list[str]:
    """Validate an app display name."""
    errors = []
    stripped = name.strip()
    if len(stripped) < MIN_LENGTH:
        errors.append(f"Name must be at least {MIN_LENGTH} characters")
    if len(stripped) > MAX_LENGTH:
        errors.append(f"Name must be at most {MAX_LENGTH} characters")
    if stripped in RESERVED_NAMES:
        errors.append(f"Name '{stripped}' is reserved")
    for pattern in PROFANITY_PATTERNS:
        if pattern.search(stripped):
            errors.append("Name contains inappropriate language")
            break
    return errors

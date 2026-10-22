"""Content policy — enforce marketplace listing guidelines."""

import re

FORBIDDEN_WORDS = {"hack", "crack", "keygen", "warez", "exploit"}
MAX_NAME_LENGTH = 50
MAX_DESCRIPTION_LENGTH = 2000


def validate_listing_content(*, name: str, description: str, tags: list[str]) -> dict:
    violations = []
    if len(name) > MAX_NAME_LENGTH:
        violations.append(f"Name exceeds {MAX_NAME_LENGTH} chars")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        violations.append(f"Description exceeds {MAX_DESCRIPTION_LENGTH} chars")
    combined = f"{name} {description} {' '.join(tags)}".lower()
    for word in FORBIDDEN_WORDS:
        if word in combined:
            violations.append(f"Forbidden content: '{word}'")
    if re.search(r'https?://(?!openskill\.dev)', combined):
        violations.append("External links not allowed in listing")
    if len(tags) > 10:
        violations.append("Maximum 10 tags allowed")
    return {"compliant": len(violations) == 0, "violations": violations}


def sanitize_html(*, content: str) -> str:
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'on\w+\s*=\s*"[^"]*"', '', content, flags=re.IGNORECASE)
    content = re.sub(r"on\w+\s*=\s*'[^']*'", '', content, flags=re.IGNORECASE)
    return content.strip()

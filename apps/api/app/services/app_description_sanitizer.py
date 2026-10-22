"""App description sanitizer — strip dangerous content from descriptions."""

import re

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<script.*?>.*?</script>", re.I | re.S)
MAX_DESCRIPTION_LENGTH = 2000

def sanitize_description(text: str | None) -> str | None:
    if not text: return text
    cleaned = _SCRIPT_RE.sub("", text)
    cleaned = _HTML_TAG_RE.sub("", cleaned)
    return cleaned[:MAX_DESCRIPTION_LENGTH].strip()

def validate_description(text: str | None) -> list[str]:
    if text is None: return []
    errors = []
    if len(text) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"Description too long ({len(text)}, max {MAX_DESCRIPTION_LENGTH})")
    if _SCRIPT_RE.search(text):
        errors.append("Description contains script tags")
    return errors

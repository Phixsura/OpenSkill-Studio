"""Tag input validator — validate and normalize tags for apps and resources."""
from __future__ import annotations
import re
import html

TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,30}[a-z0-9]$")
MAX_TAGS = 20


def validate_tag(tag: str) -> dict:
    normalized = tag.strip().lower().replace(" ", "-")
    if not TAG_RE.match(normalized):
        return {"valid": False, "tag": tag, "normalized": normalized,
                "error": "Tags must be 2-32 lowercase alphanumeric with hyphens"}
    return {"valid": True, "tag": normalized, "normalized": normalized}


def validate_tags(tags: list[str]) -> dict:
    if len(tags) > MAX_TAGS:
        return {"valid": False, "error": f"Max {MAX_TAGS} tags allowed", "count": len(tags)}
    results = [validate_tag(t) for t in tags]
    valid = [r["normalized"] for r in results if r["valid"]]
    invalid = [r for r in results if not r["valid"]]
    unique = list(dict.fromkeys(valid))  # deduplicate preserving order
    return {"valid": len(invalid) == 0, "tags": unique, "count": len(unique),
            "invalid": invalid, "duplicates_removed": len(valid) - len(unique)}


def suggest_tags(prefix: str, available: list[str]) -> list[str]:
    p = prefix.lower()
    return [t for t in available if t.startswith(p)][:5]

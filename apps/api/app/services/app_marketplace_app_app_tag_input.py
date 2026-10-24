"""Tag input — tag management with validation and suggestions."""

import html
import re

TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,29}$")
MAX_TAGS = 10

SUGGESTED_TAGS = [
    "productivity", "developer-tools", "analytics", "automation", "integrations",
    "security", "monitoring", "communication", "ai-ml", "data",
]


def validate_tag(*, tag: str) -> dict:
    t = tag.strip().lower()
    if not TAG_RE.match(t):
        return {"valid": False, "tag": t, "error": "Tags: lowercase, digits, hyphens, 1-30 chars"}
    return {"valid": True, "tag": t}


def validate_tags(*, tags: list[str]) -> dict:
    results = [validate_tag(tag=t) for t in tags]
    valid = [r["tag"] for r in results if r["valid"]]
    invalid = [r for r in results if not r["valid"]]
    if len(valid) > MAX_TAGS:
        return {"valid": False, "error": f"Maximum {MAX_TAGS} tags", "tags": valid[:MAX_TAGS]}
    unique = list(dict.fromkeys(valid))
    return {"valid": len(invalid) == 0 and len(unique) <= MAX_TAGS,
            "tags": unique, "duplicates_removed": len(valid) - len(unique),
            "invalid": invalid}


def suggest_tags(*, query: str) -> list[str]:
    q = query.lower()
    return [t for t in SUGGESTED_TAGS if q in t][:5]

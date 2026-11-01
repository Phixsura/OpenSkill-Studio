"""Release notes — structured release note generator."""

import html
from datetime import datetime, timezone

CATEGORY_ICONS = {"feature": "✨", "fix": "🐛", "improvement": "⚡", "breaking": "💥", "security": "🔒", "docs": "📝"}


def build_release_notes(*, version: str, date: str | None = None,
                          items: list[dict]) -> dict:
    categorized: dict[str, list] = {}
    for item in items:
        cat = item.get("category", "feature")
        entry = {"title": html.escape(item.get("title", "")),
                 "description": html.escape(item.get("description", "")),
                 "icon": CATEGORY_ICONS.get(cat, "📌"),
                 "pr": item.get("pr"), "author": html.escape(item.get("author", ""))}
        categorized.setdefault(cat, []).append(entry)
    has_breaking = "breaking" in categorized
    has_security = "security" in categorized
    return {"version": version, "date": date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "categories": categorized, "total_items": len(items),
            "category_count": len(categorized),
            "has_breaking": has_breaking, "has_security": has_security}

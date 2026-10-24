"""SDK changelog — track SDK version history across all languages."""
from __future__ import annotations
import html


def build_sdk_changelog(releases: list[dict]) -> dict:
    by_language: dict[str, list[dict]] = {}
    for r in releases:
        lang = r.get("language", "")
        by_language.setdefault(lang, []).append({
            "version": r["version"], "date": r.get("date", ""),
            "changes": [html.escape(c) for c in r.get("changes", [])],
            "breaking": r.get("breaking", False),
        })
    return {"languages": list(by_language.keys()),
            "releases": by_language,
            "total_releases": len(releases),
            "latest": {lang: rels[0]["version"] for lang, rels in by_language.items() if rels}}

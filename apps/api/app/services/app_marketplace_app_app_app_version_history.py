"""App version history — version timeline with changelog links."""

import html
from datetime import datetime, timezone


def build_version_history(*, versions: list[dict]) -> dict:
    items = []
    for v in sorted(versions, key=lambda x: x.get("published_at", ""), reverse=True):
        items.append({
            "version": v["version"],
            "published_at": v.get("published_at", ""),
            "author": html.escape(v.get("author", "")),
            "change_count": v.get("change_count", 0),
            "downloads": v.get("downloads", 0),
            "is_latest": False,
            "is_prerelease": "-" in v["version"],
        })
    if items:
        items[0]["is_latest"] = True
    return {"versions": items, "total": len(items),
            "latest": items[0]["version"] if items else None,
            "prerelease_count": sum(1 for v in items if v["is_prerelease"])}

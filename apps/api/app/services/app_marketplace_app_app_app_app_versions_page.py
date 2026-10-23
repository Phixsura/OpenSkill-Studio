"""App versions page — complete version management page."""

import html


def build_versions_page(*, app_name: str, versions: list[dict],
                           current_version: str = "") -> dict:
    items = []
    for v in sorted(versions, key=lambda x: x.get("published_at", ""), reverse=True):
        ver = v["version"]
        items.append({
            "version": ver,
            "published_at": v.get("published_at", ""),
            "author": html.escape(v.get("author", "")),
            "downloads": v.get("downloads", 0),
            "change_count": v.get("change_count", 0),
            "is_current": ver == current_version,
            "is_prerelease": "-" in ver,
            "can_rollback": ver != current_version and v.get("status") == "published",
        })
    latest = items[0]["version"] if items else None
    prerelease_count = sum(1 for v in items if v["is_prerelease"])
    total_downloads = sum(v["downloads"] for v in items)
    return {"app_name": html.escape(app_name), "versions": items,
            "total": len(items), "current": current_version,
            "latest": latest, "prerelease_count": prerelease_count,
            "total_downloads": total_downloads}

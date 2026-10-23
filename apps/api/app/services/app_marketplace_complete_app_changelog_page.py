"""Complete app changelog page — full changelog with versions, diffs, and release notes."""


def build_complete_changelog_page(*, app: dict, versions: list[dict],
                                      page: int = 1, per_page: int = 10) -> dict:
    total = len(versions)
    start = (page - 1) * per_page
    page_versions = versions[start:start + per_page]
    entries = []
    for v in page_versions:
        entries.append({
            "version": v["version"], "released_at": v.get("released_at", ""),
            "changes": v.get("changes", []), "change_count": len(v.get("changes", [])),
            "has_breaking": v.get("has_breaking", False),
            "release_notes": v.get("release_notes", ""),
        })
    total_changes = sum(len(v.get("changes", [])) for v in versions)
    breaking_count = sum(1 for v in versions if v.get("has_breaking"))
    return {
        "page_type": "app_changelog",
        "app": {"id": app["id"], "name": app["name"]},
        "entries": entries,
        "stats": {"total_versions": total, "total_changes": total_changes, "breaking_releases": breaking_count},
        "pagination": {"page": page, "total": total, "total_pages": max(1, (total + per_page - 1) // per_page)},
        "latest_version": versions[0]["version"] if versions else None,
        "rss_url": f"/marketplace/apps/{app.get('slug', app['id'])}/changelog.rss",
    }

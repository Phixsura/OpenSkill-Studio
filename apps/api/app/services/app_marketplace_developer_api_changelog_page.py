"""Developer API changelog page — track all API changes with migration guides."""


def build_api_changelog_page(*, versions: list[dict]) -> dict:
    entries = []
    for v in versions:
        added = v.get("endpoints_added", [])
        removed = v.get("endpoints_removed", [])
        modified = v.get("endpoints_modified", [])
        entries.append({
            "version": v["version"], "date": v.get("date", ""),
            "added": len(added), "removed": len(removed), "modified": len(modified),
            "breaking": len(removed) > 0,
            "total_changes": len(added) + len(removed) + len(modified),
            "migration_guide": v.get("migration_guide"),
        })
    breaking_count = sum(1 for e in entries if e["breaking"])
    return {
        "page_type": "api_changelog",
        "entries": entries,
        "total_versions": len(entries),
        "breaking_releases": breaking_count,
        "latest": entries[0]["version"] if entries else None,
        "stability_score": round(max(0, 100 - breaking_count * 15), 1),
    }

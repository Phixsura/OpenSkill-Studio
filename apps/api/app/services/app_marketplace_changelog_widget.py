"""Changelog widget — embeddable changelog for app listing pages."""


def build_changelog_widget(*, app_name: str, versions: list[dict], max_entries: int = 5) -> dict:
    entries = []
    for v in versions[:max_entries]:
        entry = {"version": v["version"], "date": v.get("released_at", ""),
                  "highlights": []}
        for change in v.get("changes", [])[:3]:
            entry["highlights"].append({"type": change.get("type", "misc"),
                                          "text": change.get("description", "")})
        entry["total_changes"] = len(v.get("changes", []))
        entries.append(entry)
    return {"app_name": app_name, "entries": entries, "showing": len(entries),
            "total_versions": len(versions), "has_more": len(versions) > max_entries}


def get_latest_changes(*, versions: list[dict], limit: int = 10) -> list[dict]:
    all_changes = []
    for v in versions:
        for c in v.get("changes", []):
            all_changes.append({**c, "version": v["version"], "date": v.get("released_at", "")})
    return sorted(all_changes, key=lambda c: c.get("date", ""), reverse=True)[:limit]

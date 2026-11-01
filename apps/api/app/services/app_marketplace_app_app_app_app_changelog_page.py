"""App changelog page — complete changelog page with version filter."""

import html


def build_changelog_page(*, app_name: str, releases: list[dict],
                            filter_type: str | None = None) -> dict:
    items = []
    type_counts: dict[str, int] = {}
    for rel in sorted(releases, key=lambda r: r.get("date", ""), reverse=True):
        entries = []
        for e in rel.get("entries", []):
            t = e.get("type", "changed")
            type_counts[t] = type_counts.get(t, 0) + 1
            if filter_type and t != filter_type:
                continue
            entries.append({"type": t, "text": html.escape(e.get("text", "")),
                             "icon": {"added": "✨", "fixed": "🐛", "changed": "🔄",
                                       "removed": "🗑️", "security": "🔒"}.get(t, "📌")})
        if entries or not filter_type:
            items.append({
                "version": rel["version"], "date": rel.get("date", ""),
                "entries": entries, "entry_count": len(entries),
                "has_breaking": any(e.get("type") == "removed" for e in entries),
            })
    total_entries = sum(v for v in type_counts.values())
    return {"app_name": html.escape(app_name), "releases": items,
            "total_releases": len(items), "total_entries": total_entries,
            "type_counts": type_counts, "filter": filter_type,
            "available_filters": sorted(type_counts.keys())}

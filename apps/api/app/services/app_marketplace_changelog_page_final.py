"""Changelog page FINAL — the complete platform changelog with all features."""


def build_changelog_page_final(*, platform_updates: list[dict], app_updates: list[dict],
                                    api_changes: list[dict], filter_type: str | None = None) -> dict:
    all_entries = []
    for u in platform_updates:
        all_entries.append({**u, "entry_type": "platform"})
    for u in app_updates:
        all_entries.append({**u, "entry_type": "app"})
    for u in api_changes:
        all_entries.append({**u, "entry_type": "api"})
    all_entries.sort(key=lambda e: e.get("date", ""), reverse=True)
    if filter_type:
        all_entries = [e for e in all_entries if e["entry_type"] == filter_type]
    return {
        "page_type": "platform_changelog",
        "entries": all_entries[:50],
        "total": len(all_entries),
        "filter_options": ["all", "platform", "app", "api"],
        "active_filter": filter_type or "all",
        "rss_url": "/changelog.rss",
    }

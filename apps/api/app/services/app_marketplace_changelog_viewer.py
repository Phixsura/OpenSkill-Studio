"""Changelog viewer — paginated, filterable changelog for app versions."""


def get_changelog_page(*, entries: list[dict], page: int = 1, per_page: int = 10,
                          type_filter: str | None = None) -> dict:
    filtered = entries
    if type_filter:
        filtered = [e for e in filtered if type_filter in [c.get("type") for c in e.get("changes", [])]]
    total = len(filtered)
    start = (page - 1) * per_page
    page_entries = filtered[start:start + per_page]
    return {"entries": page_entries, "total": total, "page": page, "per_page": per_page,
            "total_pages": max(1, (total + per_page - 1) // per_page), "has_next": start + per_page < total}


def get_changelog_summary(*, entries: list[dict]) -> dict:
    total_changes = sum(len(e.get("changes", [])) for e in entries)
    breaking = sum(1 for e in entries if e.get("has_breaking"))
    return {"total_versions": len(entries), "total_changes": total_changes,
            "breaking_versions": breaking, "latest": entries[0].get("version") if entries else None}


def search_changelog(*, entries: list[dict], query: str) -> list[dict]:
    q = query.lower()
    results = []
    for e in entries:
        for c in e.get("changes", []):
            if q in c.get("description", "").lower():
                results.append({"version": e.get("version"), "change": c})
    return results

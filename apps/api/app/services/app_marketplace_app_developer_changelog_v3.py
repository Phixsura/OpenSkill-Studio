"""Developer changelog v3 — interactive changelog with diff highlighting."""


def build_interactive_changelog(*, versions: list[dict]) -> dict:
    entries = []
    for i, v in enumerate(versions):
        prev = versions[i + 1] if i + 1 < len(versions) else None
        entries.append({
            "version": v["version"], "released_at": v.get("released_at"),
            "changes": v.get("changes", []), "change_count": len(v.get("changes", [])),
            "has_breaking": any(c.get("breaking") for c in v.get("changes", [])),
            "previous_version": prev["version"] if prev else None,
        })
    return {"entries": entries, "total_versions": len(entries),
            "latest": entries[0]["version"] if entries else None}


def filter_changelog(*, entries: list[dict], breaking_only: bool = False,
                       category: str | None = None) -> list[dict]:
    result = entries
    if breaking_only:
        result = [e for e in result if e.get("has_breaking")]
    if category:
        result = [e for e in result if any(c.get("category") == category for c in e.get("changes", []))]
    return result

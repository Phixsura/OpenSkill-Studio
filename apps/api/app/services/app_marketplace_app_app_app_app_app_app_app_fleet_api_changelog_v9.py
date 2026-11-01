"""Fleet API Changelog v9 — track API version changelog management."""
from __future__ import annotations
def fleet_api_changelog_v9(apis: list[dict]) -> dict:
    with_changelog = [a for a in apis if a.get("has_changelog")]
    entries = sum(a.get("changelog_entries", 0) for a in apis)
    breaking = sum(a.get("breaking_changes", 0) for a in apis)
    return {"apis": len(apis), "with_changelog": len(with_changelog), "total_entries": entries,
            "breaking_changes": breaking, "healthy": len(with_changelog) == len(apis)}

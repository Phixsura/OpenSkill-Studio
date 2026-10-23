"""API changelog tracker — track breaking and non-breaking API changes."""
from __future__ import annotations
import html


CHANGE_TYPES = {"added", "deprecated", "removed", "changed", "fixed"}


def record_change(version: str, change_type: str, endpoint: str,
                  description: str, breaking: bool = False) -> dict:
    if change_type not in CHANGE_TYPES:
        return {"recorded": False, "error": f"invalid type, use {sorted(CHANGE_TYPES)}"}
    return {"recorded": True, "version": version, "type": change_type,
            "endpoint": endpoint, "description": html.escape(description),
            "breaking": breaking}


def build_api_changelog(changes: list[dict]) -> dict:
    by_version: dict[str, list[dict]] = {}
    breaking_count = 0
    for c in changes:
        v = c.get("version", "unknown")
        by_version.setdefault(v, []).append(c)
        if c.get("breaking"):
            breaking_count += 1
    versions = sorted(by_version.keys(), reverse=True)
    return {"versions": {v: by_version[v] for v in versions},
            "total_changes": len(changes), "breaking_count": breaking_count,
            "version_count": len(versions), "has_breaking": breaking_count > 0}

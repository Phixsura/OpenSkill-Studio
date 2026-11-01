"""Service changelog — track service changes across versions."""
from __future__ import annotations

def build_changelog(changes: list[dict]) -> dict:
    by_version: dict[str, list[dict]] = {}
    for c in changes:
        v = c.get("version", "unreleased")
        by_version.setdefault(v, []).append({"type": c["type"], "description": c["description"]})
    return {"versions": by_version, "total_changes": len(changes),
            "version_count": len(by_version)}

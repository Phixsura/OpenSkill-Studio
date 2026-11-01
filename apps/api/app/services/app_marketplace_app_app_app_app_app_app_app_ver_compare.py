"""App version comparison — compare features between app versions."""
from __future__ import annotations
import html


def compare_versions(v1: dict, v2: dict) -> dict:
    v1_features = set(v1.get("features", []))
    v2_features = set(v2.get("features", []))
    added = sorted(v2_features - v1_features)
    removed = sorted(v1_features - v2_features)
    unchanged = sorted(v1_features & v2_features)
    return {
        "from_version": v1.get("version", ""),
        "to_version": v2.get("version", ""),
        "added": added, "added_count": len(added),
        "removed": removed, "removed_count": len(removed),
        "unchanged": unchanged, "unchanged_count": len(unchanged),
        "breaking": len(removed) > 0,
        "summary": f"+{len(added)} -{len(removed)} ={len(unchanged)}",
    }

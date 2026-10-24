"""Platform release notes generator — generate release notes from commits."""
from __future__ import annotations


def generate_release_notes(commits: list[dict], version: str) -> dict:
    features = []
    fixes = []
    breaking = []
    other = []
    for c in commits:
        msg = c.get("message", "")
        if msg.startswith("feat"):
            features.append(msg)
        elif msg.startswith("fix"):
            fixes.append(msg)
        elif "BREAKING" in msg.upper():
            breaking.append(msg)
        else:
            other.append(msg)
    return {"version": version, "features": features, "fixes": fixes,
            "breaking_changes": breaking, "other": other,
            "total_commits": len(commits),
            "has_breaking": len(breaking) > 0}


def compare_releases(v1: dict, v2: dict) -> dict:
    return {"from_version": v1.get("version", ""),
            "to_version": v2.get("version", ""),
            "new_features": v2.get("features", []),
            "new_fixes": v2.get("fixes", []),
            "breaking": v2.get("breaking_changes", []),
            "upgrade_risk": "high" if v2.get("has_breaking") else "low"}

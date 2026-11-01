"""Fleet AI Changelog — track AI platform release notes and changes."""
from __future__ import annotations
def fleet_ai_changelog(changelogs: list[dict]) -> dict:
    active = [c for c in changelogs if c.get("active", True)]
    releases = sum(c.get("releases", 0) for c in changelogs)
    features = sum(c.get("features", 0) for c in changelogs)
    fixes = sum(c.get("fixes", 0) for c in changelogs)
    subscribers = sum(c.get("subscribers", 0) for c in changelogs)
    return {"changelogs": len(changelogs), "active": len(active), "releases": releases,
            "features": features, "fixes": fixes, "subscribers": subscribers, "informative": releases > 0}

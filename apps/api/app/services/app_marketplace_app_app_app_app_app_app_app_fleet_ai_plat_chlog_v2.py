"""Fleet AI Platform Changelog v2 — track automated platform release notes."""
from __future__ import annotations
def fleet_ai_platform_changelog_v2(logs: list[dict]) -> dict:
    active = [l for l in logs if l.get("active", True)]
    releases = sum(l.get("releases", 0) for l in logs)
    features = sum(l.get("features", 0) for l in logs)
    fixes = sum(l.get("fixes", 0) for l in logs)
    subscribers = sum(l.get("subscribers", 0) for l in logs)
    return {"logs": len(logs), "active": len(active), "releases": releases,
            "features": features, "fixes": fixes, "subscribers": subscribers, "publishing": releases > 0}

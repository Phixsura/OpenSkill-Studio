"""Version tracker — track platform component versions and update availability."""
from __future__ import annotations


def check_versions(components: list[dict]) -> dict:
    results = []
    updates_available = 0
    for c in components:
        current = c.get("current", "0.0.0")
        latest = c.get("latest", current)
        up_to_date = current == latest
        if not up_to_date:
            updates_available += 1
        results.append({
            "name": c["name"], "current": current, "latest": latest,
            "up_to_date": up_to_date,
            "update_type": _classify_update(current, latest) if not up_to_date else None,
        })
    return {
        "components": results, "total": len(results),
        "up_to_date": len(results) - updates_available,
        "updates_available": updates_available,
        "all_current": updates_available == 0,
    }


def _classify_update(current: str, latest: str) -> str:
    cur = current.split(".")
    lat = latest.split(".")
    if len(cur) >= 1 and len(lat) >= 1 and cur[0] != lat[0]:
        return "major"
    if len(cur) >= 2 and len(lat) >= 2 and cur[1] != lat[1]:
        return "minor"
    return "patch"

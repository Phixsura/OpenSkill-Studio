"""Dependency update checker — find outdated packages."""
from __future__ import annotations


def check_updates(deps: list[dict]) -> dict:
    outdated = []
    up_to_date = 0
    for d in deps:
        current = d.get("current", "0.0.0")
        latest = d.get("latest", current)
        if current != latest:
            update_type = "major" if current.split(".")[0] != latest.split(".")[0] else \
                          "minor" if current.split(".")[1] != latest.split(".")[1] else "patch"
            outdated.append({"name": d["name"], "current": current, "latest": latest,
                              "type": update_type, "breaking": update_type == "major"})
        else:
            up_to_date += 1
    return {"outdated": outdated, "outdated_count": len(outdated),
            "up_to_date": up_to_date, "total": len(deps),
            "has_major": any(o["type"] == "major" for o in outdated)}


def prioritize_updates(outdated: list[dict]) -> list[dict]:
    priority = {"major": 3, "minor": 2, "patch": 1}
    return sorted(outdated, key=lambda o: -priority.get(o["type"], 0))

"""Dependency update — check and apply dependency updates."""


def check_updates(*, dependencies: list[dict]) -> dict:
    updates = []
    for dep in dependencies:
        current = dep.get("current_version", "0.0.0")
        latest = dep.get("latest_version", current)
        if current != latest:
            major_curr = int(current.split(".")[0])
            major_latest = int(latest.split(".")[0])
            update_type = "major" if major_latest > major_curr else "minor" if latest > current else "patch"
            updates.append({
                "name": dep["name"],
                "current": current,
                "latest": latest,
                "type": update_type,
                "breaking": update_type == "major",
            })
    return {
        "total_deps": len(dependencies),
        "updates_available": len(updates),
        "updates": updates,
        "breaking_count": sum(1 for u in updates if u["breaking"]),
        "up_to_date": len(updates) == 0,
    }

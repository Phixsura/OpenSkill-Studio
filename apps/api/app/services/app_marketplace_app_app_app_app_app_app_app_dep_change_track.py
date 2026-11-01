"""Dependency change tracker — track when service dependencies change."""
from __future__ import annotations


def track_dep_changes(before: dict[str, list[str]], after: dict[str, list[str]]) -> dict:
    changes = []
    all_services = set(before.keys()) | set(after.keys())
    for svc in sorted(all_services):
        old_deps = set(before.get(svc, []))
        new_deps = set(after.get(svc, []))
        added = sorted(new_deps - old_deps)
        removed = sorted(old_deps - new_deps)
        if added or removed:
            changes.append({"service": svc, "added": added, "removed": removed,
                            "risk": "high" if removed else "low"})
    return {"changes": changes, "services_affected": len(changes),
            "total_added": sum(len(c["added"]) for c in changes),
            "total_removed": sum(len(c["removed"]) for c in changes),
            "has_removals": any(c["removed"] for c in changes)}

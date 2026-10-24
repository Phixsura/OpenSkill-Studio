"""Incident correlation — correlate incidents across services by time proximity."""
from __future__ import annotations
from collections import defaultdict


def correlate_incidents(incidents: list[dict], window_seconds: int = 300) -> dict:
    sorted_inc = sorted(incidents, key=lambda i: i.get("timestamp", 0))
    groups = []
    current_group: list[dict] = []
    for inc in sorted_inc:
        if not current_group:
            current_group = [inc]
        elif inc["timestamp"] - current_group[-1]["timestamp"] <= window_seconds:
            current_group.append(inc)
        else:
            if len(current_group) > 1:
                groups.append({"incidents": current_group, "services": list(set(i["service"] for i in current_group)),
                                "count": len(current_group)})
            current_group = [inc]
    if len(current_group) > 1:
        groups.append({"incidents": current_group, "services": list(set(i["service"] for i in current_group)),
                        "count": len(current_group)})
    return {"correlated_groups": len(groups), "total_incidents": len(incidents),
            "groups": groups, "uncorrelated": len(incidents) - sum(g["count"] for g in groups)}

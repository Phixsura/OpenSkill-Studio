"""Incident correlation — find related incidents and root causes."""
from __future__ import annotations


def correlate_incidents(incidents: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for inc in incidents:
        for tag in inc.get("tags", []):
            groups.setdefault(tag, []).append(inc)
    correlations = []
    for tag, group in groups.items():
        if len(group) >= 2:
            correlations.append({"tag": tag, "incidents": [i["id"] for i in group],
                                  "count": len(group)})
    correlations.sort(key=lambda c: -c["count"])
    return {"correlations": correlations, "total_incidents": len(incidents),
            "correlated_groups": len(correlations),
            "has_correlations": len(correlations) > 0}


def suggest_root_cause(correlation: dict) -> dict:
    count = correlation.get("count", 0)
    tag = correlation.get("tag", "")
    if count >= 5:
        confidence = "high"
    elif count >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    return {"tag": tag, "affected_incidents": count,
            "confidence": confidence,
            "suggestion": f"Investigate '{tag}' — {count} related incidents"}

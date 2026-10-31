"""Feature adoption tracker — track feature adoption rates over time."""
from __future__ import annotations
from collections import defaultdict


def track_adoption(events: list[dict], total_users: int) -> dict:
    by_feature: dict[str, set] = defaultdict(set)
    for e in events:
        by_feature[e["feature"]].add(e["user_id"])
    features = []
    for feat, users in sorted(by_feature.items()):
        adoption_pct = round(len(users) / max(total_users, 1) * 100, 1)
        features.append({"feature": feat, "unique_users": len(users),
                          "adoption_pct": adoption_pct})
    features.sort(key=lambda f: -f["adoption_pct"])
    return {"features": features, "total_users": total_users,
            "features_tracked": len(features)}


def adoption_funnel(steps: list[dict]) -> dict:
    if not steps:
        return {"steps": [], "completion_pct": 0}
    results = []
    for i, step in enumerate(steps):
        drop_off = round((1 - step["count"] / max(steps[0]["count"], 1)) * 100, 1) if i > 0 else 0
        results.append({"step": step["name"], "count": step["count"], "drop_off_pct": drop_off})
    completion = round(steps[-1]["count"] / max(steps[0]["count"], 1) * 100, 1)
    return {"steps": results, "completion_pct": completion}

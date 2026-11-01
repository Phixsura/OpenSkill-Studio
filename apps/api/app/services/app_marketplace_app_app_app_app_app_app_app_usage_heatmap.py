"""Feature usage heatmap — track feature adoption by time."""
from __future__ import annotations


def build_heatmap(events: list[dict], features: list[str]) -> dict:
    grid: dict[str, dict[str, int]] = {f: {} for f in features}
    for e in events:
        feat = e.get("feature", "")
        hour = e.get("hour", "00")
        if feat in grid:
            grid[feat][hour] = grid[feat].get(hour, 0) + 1
    total = sum(sum(hours.values()) for hours in grid.values())
    hottest = None
    max_count = 0
    for feat, hours in grid.items():
        for h, c in hours.items():
            if c > max_count:
                max_count = c
                hottest = {"feature": feat, "hour": h, "count": c}
    return {"grid": grid, "features": features, "total_events": total,
            "hottest": hottest}


def feature_adoption(events: list[dict], feature_list: list[str]) -> dict:
    users_by_feature: dict[str, set] = {f: set() for f in feature_list}
    total_users: set = set()
    for e in events:
        uid = e.get("user_id", "")
        feat = e.get("feature", "")
        total_users.add(uid)
        if feat in users_by_feature:
            users_by_feature[feat].add(uid)
    adoption = {}
    for f in feature_list:
        pct = round(len(users_by_feature[f]) / max(len(total_users), 1) * 100, 1)
        adoption[f] = {"users": len(users_by_feature[f]), "pct": pct}
    return {"adoption": adoption, "total_users": len(total_users)}

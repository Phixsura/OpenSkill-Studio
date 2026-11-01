"""Feature usage heatmap — visualize which features are used most by time of day."""
from __future__ import annotations


def build_heatmap(events: list[dict], *, features: list[str] | None = None) -> dict:
    grid: dict[str, list[int]] = {}
    all_features = set()
    for e in events:
        feat = e.get("feature", "unknown")
        hour = e.get("hour", 0)
        all_features.add(feat)
        if feat not in grid:
            grid[feat] = [0] * 24
        if 0 <= hour < 24:
            grid[feat][hour] += 1
    if features:
        grid = {k: v for k, v in grid.items() if k in features}
    peak_hour = 0
    peak_count = 0
    for hours in grid.values():
        for h, c in enumerate(hours):
            if c > peak_count:
                peak_count = c
                peak_hour = h
    rows = []
    for feat in sorted(grid):
        total = sum(grid[feat])
        rows.append({"feature": feat, "hours": grid[feat], "total": total,
                      "peak_hour": grid[feat].index(max(grid[feat])) if max(grid[feat]) > 0 else 0})
    return {"features": rows, "total_features": len(rows), "total_events": len(events),
            "peak_hour": peak_hour, "peak_hour_display": f"{peak_hour:02d}:00"}


def top_features(events: list[dict], *, limit: int = 5) -> list[dict]:
    counts: dict[str, int] = {}
    for e in events:
        f = e.get("feature", "unknown")
        counts[f] = counts.get(f, 0) + 1
    total = len(events)
    ranked = sorted(counts.items(), key=lambda x: -x[1])[:limit]
    return [{"feature": f, "count": c, "pct": round(c / max(total, 1) * 100, 1)} for f, c in ranked]

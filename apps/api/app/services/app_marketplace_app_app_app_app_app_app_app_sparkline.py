"""Sparkline generator — create compact inline trend indicators."""
from __future__ import annotations


def generate_sparkline(values: list[float], *, width: int = 100, height: int = 24) -> dict:
    if not values:
        return {"points": "", "trend": "flat", "min": 0, "max": 0}
    mn, mx = min(values), max(values)
    rng = mx - mn or 1
    n = len(values)
    points = []
    for i, v in enumerate(values):
        x = round(i / max(n - 1, 1) * width, 1)
        y = round(height - (v - mn) / rng * height, 1)
        points.append(f"{x},{y}")
    first, last = values[0], values[-1]
    trend = "up" if last > first * 1.05 else "down" if last < first * 0.95 else "flat"
    change_pct = round((last - first) / max(abs(first), 0.01) * 100, 1)
    return {
        "points": " ".join(points), "polyline": " ".join(points),
        "width": width, "height": height,
        "min": round(mn, 2), "max": round(mx, 2),
        "current": round(last, 2), "trend": trend,
        "change_pct": change_pct,
    }

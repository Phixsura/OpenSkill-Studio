"""Platform activity heatmap — aggregate user activity by day of week and hour."""
from __future__ import annotations

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def build_activity_heatmap(events: list[dict]) -> dict:
    grid: list[list[int]] = [[0] * 24 for _ in range(7)]
    for e in events:
        day = e.get("day", 0)  # 0=Mon
        hour = e.get("hour", 0)
        if 0 <= day < 7 and 0 <= hour < 24:
            grid[day][hour] += 1
    max_val = max(max(row) for row in grid) if events else 1
    peak_day, peak_hour, peak_val = 0, 0, 0
    for d in range(7):
        for h in range(24):
            if grid[d][h] > peak_val:
                peak_val = grid[d][h]
                peak_day, peak_hour = d, h
    rows = [{"day": DAYS[d], "hours": grid[d], "total": sum(grid[d])} for d in range(7)]
    return {
        "grid": rows, "max_value": max_val,
        "total_events": len(events),
        "peak": {"day": DAYS[peak_day], "hour": peak_hour, "count": peak_val},
        "peak_display": f"{DAYS[peak_day]} {peak_hour:02d}:00",
    }

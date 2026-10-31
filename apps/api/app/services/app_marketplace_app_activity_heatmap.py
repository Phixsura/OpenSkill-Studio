"""Activity heatmap — visualize user activity by hour and day of week."""


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def build_activity_heatmap(*, events: list[dict]) -> dict:
    grid: dict[str, dict[int, int]] = {d: {h: 0 for h in range(24)} for d in DAYS}
    for event in events:
        day = event.get("day_of_week", "Mon")
        hour = event.get("hour", 0)
        if day in grid and 0 <= hour < 24:
            grid[day][hour] += 1
    max_val = max((v for row in grid.values() for v in row.values()), default=1) or 1
    cells = []
    for day in DAYS:
        for hour in range(24):
            count = grid[day][hour]
            cells.append({
                "day": day, "hour": hour, "count": count,
                "intensity": round(count / max_val * 100, 1),
            })
    peak_cell = max(cells, key=lambda c: c["count"])
    total = sum(c["count"] for c in cells)
    return {
        "cells": cells,
        "total_events": total,
        "peak": {"day": peak_cell["day"], "hour": peak_cell["hour"], "count": peak_cell["count"]},
        "days": DAYS,
        "hours": list(range(24)),
    }

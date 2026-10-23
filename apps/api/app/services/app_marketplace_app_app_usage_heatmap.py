"""Usage heatmap — hourly/daily usage pattern visualization."""

from collections import defaultdict


def build_heatmap(*, events: list[dict]) -> dict:
    grid: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for e in events:
        ts = e.get("timestamp", "")
        if len(ts) >= 13:
            try:
                hour = int(ts[11:13])
                day = int(ts[8:10]) % 7  # simplified day-of-week
                grid[day][hour] += 1
            except (ValueError, IndexError):
                continue
    cells = []
    max_val = 0
    for day in range(7):
        for hour in range(24):
            val = grid[day][hour]
            max_val = max(max_val, val)
            cells.append({"day": day, "hour": hour, "count": val})
    for c in cells:
        c["intensity"] = round(c["count"] / max(max_val, 1) * 100)
    total = sum(c["count"] for c in cells)
    peak = max(cells, key=lambda c: c["count"])
    return {"cells": cells, "total_events": total, "peak_hour": peak["hour"],
            "peak_day": peak["day"], "peak_count": peak["count"]}

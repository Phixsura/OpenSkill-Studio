"""API usage heatmap — visualize API call patterns by hour and day."""

from collections import defaultdict


def build_usage_heatmap(*, api_calls: list[dict]) -> dict:
    grid = defaultdict(lambda: defaultdict(int))
    for call in api_calls:
        ts = call.get("timestamp", "")
        if len(ts) >= 13:
            # Extract day of week (0=Mon) and hour
            day = call.get("day_of_week", 0)
            hour = int(ts[11:13])
            grid[day][hour] += 1
    rows = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for d in range(7):
        row = {"day": days[d], "hours": [grid[d][h] for h in range(24)],
               "total": sum(grid[d][h] for h in range(24))}
        rows.append(row)
    peak_hour = max(range(24), key=lambda h: sum(grid[d][h] for d in range(7)))
    return {"rows": rows, "peak_hour": peak_hour, "total_calls": sum(r["total"] for r in rows)}


def find_quiet_hours(*, heatmap: dict, threshold_pct: float = 10) -> list[int]:
    total = max(heatmap.get("total_calls", 1), 1)
    hourly = defaultdict(int)
    for row in heatmap.get("rows", []):
        for h, count in enumerate(row.get("hours", [])):
            hourly[h] += count
    return sorted([h for h in range(24) if hourly[h] / total * 100 < threshold_pct])

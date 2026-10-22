"""Activity heatmap — hourly/daily usage patterns for developer analytics."""

from collections import defaultdict


def build_heatmap(*, events: list[dict]) -> dict:
    grid = defaultdict(lambda: defaultdict(int))
    for e in events:
        ts = e.get("timestamp", "")
        if len(ts) >= 13:
            day = ts[:10]
            hour = int(ts[11:13])
            grid[day][hour] += 1
    rows = []
    for day in sorted(grid.keys()):
        row = {"date": day, "hours": {str(h): grid[day][h] for h in range(24)}}
        row["total"] = sum(grid[day].values())
        rows.append(row)
    return {"rows": rows, "total_events": sum(r["total"] for r in rows)}


def find_peak_hours(*, heatmap: dict) -> list[dict]:
    hourly = defaultdict(int)
    for row in heatmap.get("rows", []):
        for h, count in row.get("hours", {}).items():
            hourly[int(h)] += count
    sorted_hours = sorted(hourly.items(), key=lambda x: -x[1])
    return [{"hour": h, "count": c} for h, c in sorted_hours[:5]]

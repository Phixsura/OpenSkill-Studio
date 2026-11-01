"""Resource usage timeline — historical resource consumption over time."""


def build_usage_timeline(*, data_points: list[dict]) -> dict:
    if not data_points:
        return {"timeline": [], "total_points": 0}
    resources = set()
    for dp in data_points:
        resources.update(k for k in dp if k != "timestamp")
    timeline = []
    for dp in data_points:
        entry = {"timestamp": dp.get("timestamp", "")}
        for res in resources:
            entry[res] = dp.get(res, 0)
        timeline.append(entry)
    # Calculate peaks and averages
    stats = {}
    for res in resources:
        values = [dp.get(res, 0) for dp in data_points]
        stats[res] = {
            "peak": max(values),
            "avg": round(sum(values) / len(values), 1),
            "current": values[-1] if values else 0,
        }
    return {"timeline": timeline, "total_points": len(timeline),
            "resources": sorted(resources), "stats": stats}

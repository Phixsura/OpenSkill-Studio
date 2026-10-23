"""Developer leaderboard — rank developers by various metrics."""


def build_leaderboard(*, developers: list[dict], metric: str = "installs",
                        period: str = "all_time", limit: int = 10) -> dict:
    valid_metrics = {"installs", "revenue", "rating", "apps_published", "reviews_received"}
    if metric not in valid_metrics:
        return {"error": f"Invalid metric. Valid: {', '.join(sorted(valid_metrics))}"}
    sorted_devs = sorted(developers, key=lambda d: d.get(metric, 0), reverse=True)
    ranked = []
    for i, dev in enumerate(sorted_devs[:limit], 1):
        ranked.append({
            "rank": i,
            "developer_id": dev["id"],
            "display_name": dev["name"],
            "avatar": dev.get("avatar"),
            "value": dev.get(metric, 0),
            "change": dev.get("change", 0),
        })
    return {
        "metric": metric,
        "period": period,
        "entries": ranked,
        "total_developers": len(developers),
    }

"""App leaderboard — top apps ranking by various metrics."""

import html


def build_leaderboard(*, apps: list[dict], metric: str = "downloads",
                        period: str = "all_time", limit: int = 10) -> dict:
    sorted_apps = sorted(apps, key=lambda a: a.get(metric, 0), reverse=True)[:limit]
    items = []
    for rank, app in enumerate(sorted_apps, 1):
        items.append({
            "rank": rank,
            "name": html.escape(app.get("name", "")),
            "icon": app.get("icon", "📦"),
            "value": app.get(metric, 0),
            "author": html.escape(app.get("author", "")),
            "medal": "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "",
        })
    return {"entries": items, "metric": metric, "period": period,
            "total_ranked": len(items)}

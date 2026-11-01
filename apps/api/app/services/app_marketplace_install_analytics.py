"""Install analytics — track and analyze installation patterns."""

from collections import defaultdict


def compute_install_velocity(*, daily_installs: list[dict]) -> dict:
    if len(daily_installs) < 2:
        return {"velocity": 0, "trend": "stable", "avg_daily": 0}
    counts = [d.get("count", 0) for d in daily_installs]
    avg = sum(counts) / len(counts)
    recent = sum(counts[-7:]) / min(7, len(counts))
    older = sum(counts[:-7]) / max(len(counts) - 7, 1) if len(counts) > 7 else avg
    velocity = round((recent - older) / max(older, 1) * 100, 1)
    trend = "accelerating" if velocity > 10 else "decelerating" if velocity < -10 else "stable"
    return {"velocity": velocity, "trend": trend, "avg_daily": round(avg, 1), "recent_avg": round(recent, 1)}


def compute_install_sources(*, installs: list[dict]) -> list[dict]:
    by_source = defaultdict(int)
    for inst in installs:
        by_source[inst.get("source", "direct")] += 1
    total = len(installs)
    return [{"source": s, "count": c, "pct": round(c / max(total, 1) * 100, 1)}
            for s, c in sorted(by_source.items(), key=lambda x: -x[1])]


def compute_install_funnel(*, page_views: int, detail_views: int, install_clicks: int,
                              installs_completed: int) -> dict:
    steps = [
        {"step": "Page View", "count": page_views},
        {"step": "Detail View", "count": detail_views, "rate": round(detail_views / max(page_views, 1) * 100, 1)},
        {"step": "Install Click", "count": install_clicks, "rate": round(install_clicks / max(detail_views, 1) * 100, 1)},
        {"step": "Completed", "count": installs_completed, "rate": round(installs_completed / max(install_clicks, 1) * 100, 1)},
    ]
    return {"steps": steps, "overall_rate": round(installs_completed / max(page_views, 1) * 100, 2)}

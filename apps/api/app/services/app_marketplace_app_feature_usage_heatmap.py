"""Feature usage heatmap — visualize which features users engage with most."""


def build_usage_heatmap(*, features: list[dict], days: int = 7) -> dict:
    heatmap = []
    max_usage = max((f.get("daily_usage", [0])[-1] for f in features), default=1) or 1
    for f in features:
        daily = f.get("daily_usage", [0] * days)[-days:]
        total = sum(daily)
        avg = round(total / max(len(daily), 1), 1)
        intensity = round(avg / max_usage * 100, 1)
        heatmap.append({
            "feature": f["name"],
            "category": f.get("category", "general"),
            "total_usage": total,
            "avg_daily": avg,
            "intensity_pct": intensity,
            "trend": "up" if len(daily) >= 2 and daily[-1] > daily[0] else "down" if len(daily) >= 2 and daily[-1] < daily[0] else "stable",
            "daily": daily,
        })
    heatmap.sort(key=lambda x: x["total_usage"], reverse=True)
    return {
        "features": heatmap,
        "total_features": len(heatmap),
        "most_used": heatmap[0]["feature"] if heatmap else None,
        "least_used": heatmap[-1]["feature"] if heatmap else None,
        "period_days": days,
    }

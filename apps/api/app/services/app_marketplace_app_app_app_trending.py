"""App trending — trending apps calculation based on growth metrics."""

import html


def calculate_trending(*, apps: list[dict], period: str = "7d") -> dict:
    scored = []
    for a in apps:
        current = a.get("installs_current", 0)
        previous = a.get("installs_previous", 0)
        growth = current - previous
        growth_pct = round(growth / max(previous, 1) * 100, 1) if previous else 0
        velocity = round(current / 7, 1)  # installs per day
        score = growth_pct * 0.6 + velocity * 0.4
        scored.append({
            "id": a.get("id", ""), "name": html.escape(a.get("name", "")),
            "icon": a.get("icon", "📦"), "category": a.get("category", ""),
            "growth": growth, "growth_pct": growth_pct,
            "velocity": velocity, "score": round(score, 1),
            "rating": a.get("rating", 0),
        })
    scored.sort(key=lambda x: -x["score"])
    return {"trending": scored[:10], "period": period, "total_evaluated": len(apps)}

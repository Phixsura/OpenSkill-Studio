"""App rating breakdown — detailed rating analysis with trends."""


def analyze_ratings(*, ratings: list[dict]) -> dict:
    if not ratings:
        return {"total": 0, "avg": 0, "distribution": {}, "trend": "stable"}
    total = len(ratings)
    avg = round(sum(r.get("rating", 0) for r in ratings) / total, 2)
    dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    recent = []
    for r in ratings:
        val = r.get("rating", 0)
        if val in dist:
            dist[val] += 1
        recent.append(val)
    # Trend: compare first half vs second half
    mid = total // 2
    if mid > 0:
        first_avg = sum(recent[:mid]) / mid
        second_avg = sum(recent[mid:]) / (total - mid)
        if second_avg > first_avg + 0.2:
            trend = "improving"
        elif second_avg < first_avg - 0.2:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    return {
        "total": total,
        "avg": avg,
        "distribution": dist,
        "trend": trend,
        "five_star_pct": round(dist[5] / total * 100, 1),
        "one_star_pct": round(dist[1] / total * 100, 1),
    }

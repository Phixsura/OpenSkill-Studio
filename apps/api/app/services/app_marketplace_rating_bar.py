"""Rating bar — rating distribution visualization for app reviews."""


def build_rating_bars(*, distribution: dict[str, int]) -> list[dict]:
    total = sum(distribution.values())
    bars = []
    for star in range(5, 0, -1):
        count = distribution.get(str(star), 0)
        pct = round(count / max(total, 1) * 100, 1)
        bars.append({"stars": star, "count": count, "pct": pct})
    return bars


def compute_rating_summary(*, distribution: dict[str, int]) -> dict:
    total = sum(distribution.values())
    if total == 0:
        return {"avg": 0, "total": 0, "recommendation_pct": 0}
    weighted = sum(int(star) * count for star, count in distribution.items())
    avg = round(weighted / total, 2)
    positive = sum(count for star, count in distribution.items() if int(star) >= 4)
    return {"avg": avg, "total": total, "recommendation_pct": round(positive / total * 100, 1)}

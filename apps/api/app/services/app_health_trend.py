"""App health trend — track health score changes over time."""


def compute_health_trend(scores: list[dict]) -> dict:
    """Compute health trend from timestamped scores."""
    if not scores:
        return {"trend": "stable", "current": 100, "previous": 100, "change": 0}
    current = scores[-1].get("score", 100)
    previous = scores[-2].get("score", current) if len(scores) >= 2 else current
    change = current - previous
    trend = "improving" if change > 2 else "declining" if change < -2 else "stable"
    return {"trend": trend, "current": current, "previous": previous, "change": change}

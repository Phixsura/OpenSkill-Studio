"""App health score — composite score from multiple health signals."""


def calculate_health_score(*, signals: dict) -> dict:
    weights = {
        "uptime": 30,
        "error_rate": 25,
        "latency": 20,
        "crash_free": 15,
        "user_satisfaction": 10,
    }
    scores = {}
    for key, weight in weights.items():
        raw = signals.get(key, 0)
        # Normalize: uptime/crash_free → higher is better, error_rate/latency → lower is better
        if key in ("error_rate", "latency"):
            normalized = max(100 - raw, 0)
        else:
            normalized = min(raw, 100)
        scores[key] = {"raw": raw, "normalized": round(normalized, 1),
                        "weighted": round(normalized * weight / 100, 1), "weight": weight}
    total = round(sum(s["weighted"] for s in scores.values()), 1)
    grade = "A" if total >= 90 else "B" if total >= 75 else "C" if total >= 60 else "D" if total >= 40 else "F"
    return {
        "score": total,
        "grade": grade,
        "signals": scores,
        "status": "healthy" if total >= 75 else "degraded" if total >= 50 else "unhealthy",
    }

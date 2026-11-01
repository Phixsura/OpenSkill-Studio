"""App health summary — single-number health score from all signals."""


def compute_health_summary(*, uptime_pct: float, error_rate: float, latency_p95_ms: int,
                              crash_free_pct: float, satisfaction_pct: float) -> dict:
    scores = {
        "uptime": min(uptime_pct, 100),
        "errors": max(100 - error_rate * 10, 0),
        "latency": max(100 - latency_p95_ms / 10, 0),
        "stability": min(crash_free_pct, 100),
        "satisfaction": min(satisfaction_pct, 100),
    }
    weights = {"uptime": 0.3, "errors": 0.25, "latency": 0.15, "stability": 0.2, "satisfaction": 0.1}
    total = round(sum(scores[k] * weights[k] for k in scores), 1)
    status = "excellent" if total >= 95 else "good" if total >= 80 else "fair" if total >= 60 else "poor"
    return {
        "overall_score": total,
        "status": status,
        "signals": {k: round(v, 1) for k, v in scores.items()},
        "weights": weights,
    }

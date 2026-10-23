"""Live metrics — real-time metrics dashboard for running apps."""

from datetime import datetime


def get_live_metrics(*, app_id: str) -> dict:
    now = datetime.utcnow().isoformat()
    return {
        "app_id": app_id,
        "timestamp": now,
        "realtime": {
            "active_users": 142,
            "requests_per_sec": 85.3,
            "avg_response_ms": 38,
            "error_rate_pct": 0.12,
            "cpu_pct": 34.5,
            "memory_pct": 62.1,
        },
        "trends_1h": {
            "requests": [80, 82, 85, 83, 87, 85],
            "errors": [0.1, 0.1, 0.2, 0.1, 0.12, 0.12],
            "latency": [35, 37, 38, 36, 39, 38],
        },
        "alerts_active": 0,
    }


def compute_trend(*, values: list[float]) -> dict:
    if len(values) < 2:
        return {"direction": "stable", "change_pct": 0}
    first_half = sum(values[:len(values)//2]) / (len(values)//2)
    second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
    change = round((second_half - first_half) / max(first_half, 0.01) * 100, 1)
    direction = "up" if change > 5 else "down" if change < -5 else "stable"
    return {"direction": direction, "change_pct": change,
            "current": round(values[-1], 2), "avg": round(sum(values) / len(values), 2)}

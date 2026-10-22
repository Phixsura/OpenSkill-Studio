"""Metrics collector — aggregate app performance metrics over time windows."""

from collections import defaultdict


def collect_metrics(*, data_points: list[dict]) -> dict:
    by_metric = defaultdict(list)
    for dp in data_points:
        by_metric[dp["metric"]].append(dp["value"])
    summaries = {}
    for metric, values in by_metric.items():
        summaries[metric] = {
            "count": len(values), "sum": sum(values),
            "avg": round(sum(values) / len(values), 2),
            "min": min(values), "max": max(values),
        }
    return {"metrics": summaries, "total_points": len(data_points)}


def compute_trend(*, current: float, previous: float) -> dict:
    if previous == 0:
        return {"direction": "up" if current > 0 else "flat", "change_pct": 0}
    change = round((current - previous) / abs(previous) * 100, 1)
    direction = "up" if change > 0 else "down" if change < 0 else "flat"
    return {"direction": direction, "change_pct": change}


def build_dashboard_metrics(*, installs: int, uninstalls: int, api_calls: int,
                               errors: int, avg_response_ms: float) -> dict:
    net = installs - uninstalls
    error_rate = round(errors / max(api_calls, 1) * 100, 2)
    health = "healthy" if error_rate < 1 else "degraded" if error_rate < 5 else "critical"
    return {
        "net_installs": net, "api_calls": api_calls, "error_rate": error_rate,
        "avg_response_ms": avg_response_ms, "health": health,
    }

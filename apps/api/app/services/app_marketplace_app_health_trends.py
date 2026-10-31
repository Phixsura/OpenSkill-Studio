"""Health trends — track app health metrics over time with trend detection."""

from collections import defaultdict


def compute_health_trend(*, data_points: list[dict], metric: str) -> dict:
    values = [d.get(metric, 0) for d in data_points]
    if len(values) < 2:
        return {"metric": metric, "trend": "stable", "change": 0}
    first_half = sum(values[:len(values)//2]) / max(len(values)//2, 1)
    second_half = sum(values[len(values)//2:]) / max(len(values) - len(values)//2, 1)
    if first_half == 0:
        return {"metric": metric, "trend": "up" if second_half > 0 else "stable", "change": 0}
    change = round((second_half - first_half) / first_half * 100, 1)
    trend = "improving" if change < -5 else "degrading" if change > 5 else "stable"
    return {"metric": metric, "trend": trend, "change_pct": change,
            "first_half_avg": round(first_half, 2), "second_half_avg": round(second_half, 2)}


def build_health_report(*, trends: list[dict]) -> dict:
    degrading = [t for t in trends if t.get("trend") == "degrading"]
    improving = [t for t in trends if t.get("trend") == "improving"]
    overall = "degrading" if len(degrading) > len(improving) else "improving" if improving else "stable"
    return {"overall": overall, "trends": trends, "degrading_count": len(degrading),
            "improving_count": len(improving), "needs_attention": len(degrading) > 0}


def identify_correlations(*, metrics: dict[str, list[float]]) -> list[dict]:
    correlations = []
    keys = list(metrics.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = metrics[keys[i]], metrics[keys[j]]
            if len(a) == len(b) and len(a) > 2:
                # Simple correlation check
                a_up = a[-1] > a[0]
                b_up = b[-1] > b[0]
                if a_up == b_up:
                    correlations.append({"metrics": [keys[i], keys[j]], "direction": "positive"})
                else:
                    correlations.append({"metrics": [keys[i], keys[j]], "direction": "inverse"})
    return correlations

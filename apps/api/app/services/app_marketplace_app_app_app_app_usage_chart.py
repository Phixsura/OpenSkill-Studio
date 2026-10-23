"""Usage chart — time-series usage data for dashboard charts."""

from collections import defaultdict


def build_usage_chart(*, data_points: list[dict], metric: str = "api_calls",
                        group_by: str = "day") -> dict:
    buckets: dict[str, int] = defaultdict(int)
    for dp in data_points:
        key = dp.get("date", "")[:10] if group_by == "day" else dp.get("date", "")[:7]
        buckets[key] += dp.get(metric, 0)
    labels = sorted(buckets.keys())
    values = [buckets[k] for k in labels]
    total = sum(values)
    avg = round(total / max(len(values), 1))
    peak = max(values) if values else 0
    peak_label = labels[values.index(peak)] if values and peak > 0 else None
    trend = "up" if len(values) >= 2 and values[-1] > values[0] else \
            "down" if len(values) >= 2 and values[-1] < values[0] else "flat"
    return {"labels": labels, "values": values, "metric": metric,
            "total": total, "average": avg, "peak": peak,
            "peak_label": peak_label, "trend": trend,
            "data_points": len(labels)}

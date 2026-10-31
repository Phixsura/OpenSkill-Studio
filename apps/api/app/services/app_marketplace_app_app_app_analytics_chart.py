"""App analytics chart — time-series chart data builder."""


def build_chart_data(*, data_points: list[dict], metric: str = "installs",
                       interval: str = "daily") -> dict:
    labels = [dp.get("date", "") for dp in data_points]
    values = [dp.get(metric, 0) for dp in data_points]
    total = sum(values)
    avg = round(total / max(len(values), 1), 1)
    peak = max(values) if values else 0
    peak_date = labels[values.index(peak)] if values and peak > 0 else None
    trend = "up" if len(values) >= 2 and values[-1] > values[0] else "down" if len(values) >= 2 and values[-1] < values[0] else "flat"
    return {
        "labels": labels, "values": values, "metric": metric,
        "interval": interval, "total": total, "average": avg,
        "peak": peak, "peak_date": peak_date, "trend": trend,
        "data_points": len(data_points),
    }

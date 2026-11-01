"""Metric alert — threshold-based metric alerting."""
def check_metric_alert(*, name: str, value: float, threshold: float, operator: str = "gt") -> dict:
    ops = {"gt": value > threshold, "lt": value < threshold, "gte": value >= threshold, "lte": value <= threshold}
    triggered = ops.get(operator, False)
    return {"name": name, "value": value, "threshold": threshold, "triggered": triggered,
            "status": "firing" if triggered else "ok"}

"""Metric card — individual metric display with trend."""


def build_metric_card(*, label: str, value: float, previous: float | None = None,
                        format_type: str = "number", icon: str = "📊") -> dict:
    change = round(value - previous, 2) if previous is not None else None
    change_pct = round(change / max(abs(previous), 0.01) * 100, 1) if previous and change is not None else None
    trend = None
    if change is not None:
        trend = "up" if change > 0 else "down" if change < 0 else "flat"
    return {
        "label": label, "value": value, "previous": previous,
        "change": change, "change_pct": change_pct, "trend": trend,
        "format_type": format_type, "icon": icon,
    }

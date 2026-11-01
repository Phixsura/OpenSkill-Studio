"""Metric card builder — create consistent metric cards for dashboards."""
from __future__ import annotations


def build_metric_card(*, label: str, value: float | int, unit: str = "",
                        previous: float | int | None = None,
                        icon: str = "📊", format_type: str = "number") -> dict:
    if format_type == "currency":
        display = f"${value:,.0f}" if value >= 1000 else f"${value:.2f}"
    elif format_type == "percentage":
        display = f"{value:.1f}%"
    elif format_type == "compact":
        if value >= 1_000_000:
            display = f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            display = f"{value / 1_000:.1f}K"
        else:
            display = str(int(value))
    else:
        display = f"{value:,}" if isinstance(value, int) else f"{value:,.1f}"
    delta = None
    trend = None
    if previous is not None and previous != 0:
        delta = round((value - previous) / abs(previous) * 100, 1)
        trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
    return {
        "label": label, "value": value, "display": display,
        "unit": unit, "icon": icon, "format_type": format_type,
        "delta": delta, "delta_display": f"{'+' if delta and delta > 0 else ''}{delta}%" if delta is not None else None,
        "trend": trend,
    }


def build_metric_row(metrics: list[dict]) -> list[dict]:
    return [build_metric_card(**m) for m in metrics]

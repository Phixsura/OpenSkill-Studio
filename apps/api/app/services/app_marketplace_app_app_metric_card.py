"""Metric card — KPI display with trend indicator."""

import html


def build_metric_card(*, label: str, value: float | int, unit: str = "",
                       previous: float | int | None = None, format_fn: str = "number") -> dict:
    if format_fn == "percent":
        display = f"{value:.1f}%"
    elif format_fn == "currency":
        display = f"${value:,.2f}"
    elif format_fn == "compact":
        if value >= 1_000_000:
            display = f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            display = f"{value/1_000:.1f}K"
        else:
            display = str(value)
    else:
        display = f"{value:,}"

    trend = None
    change_pct = None
    if previous is not None and previous != 0:
        change_pct = round((value - previous) / abs(previous) * 100, 1)
        trend = "up" if change_pct > 0 else "down" if change_pct < 0 else "flat"

    return {"label": html.escape(label), "value": value, "display": display,
            "unit": unit, "trend": trend, "change_pct": change_pct}

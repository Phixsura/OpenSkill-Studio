"""KPI card builder — compute key performance indicators for dashboard display."""
from __future__ import annotations


def build_kpi_cards(metrics: dict) -> list[dict]:
    cards = []
    for key, cfg in {
        "mrr": {"label": "MRR", "icon": "💰", "format": "currency", "good": "up"},
        "dau": {"label": "DAU", "icon": "👥", "format": "number", "good": "up"},
        "churn": {"label": "Churn Rate", "icon": "📉", "format": "percent", "good": "down"},
        "nps": {"label": "NPS Score", "icon": "⭐", "format": "number", "good": "up"},
        "uptime": {"label": "Uptime", "icon": "🟢", "format": "percent", "good": "up"},
        "api_calls": {"label": "API Calls", "icon": "📡", "format": "number", "good": "up"},
    }.items():
        value = metrics.get(key)
        prev = metrics.get(f"{key}_prev")
        if value is None:
            continue
        if cfg["format"] == "currency":
            display = f"${value:,.0f}"
        elif cfg["format"] == "percent":
            display = f"{value}%"
        else:
            display = f"{value:,}" if isinstance(value, int) else str(value)
        delta = None
        trend = None
        if prev is not None and prev != 0:
            delta = round((value - prev) / abs(prev) * 100, 1)
            trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
        positive = (trend == cfg["good"]) if trend else None
        cards.append({"key": key, "label": cfg["label"], "icon": cfg["icon"],
                       "value": value, "display": display, "delta": delta,
                       "delta_display": f"{'+' if delta and delta > 0 else ''}{delta}%" if delta else None,
                       "trend": trend, "positive": positive})
    return cards

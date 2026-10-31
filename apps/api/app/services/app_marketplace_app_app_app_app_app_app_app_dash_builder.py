"""Metric dashboard builder — create custom monitoring dashboards."""
from __future__ import annotations


def create_dashboard(title: str, panels: list[dict]) -> dict:
    items = []
    for i, p in enumerate(panels):
        items.append({"id": i, "title": p.get("title", ""), "type": p.get("type", "chart"),
                       "metric": p.get("metric", ""), "width": p.get("width", 6),
                       "height": p.get("height", 4)})
    return {"title": title, "panels": items, "panel_count": len(items),
            "layout": _compute_layout(items)}


def _compute_layout(panels: list[dict]) -> dict:
    total_width = sum(p["width"] for p in panels)
    rows = (total_width + 11) // 12  # 12-column grid
    return {"columns": 12, "rows": rows, "total_cells": total_width}


def dashboard_summary(dashboards: list[dict]) -> dict:
    total_panels = sum(d["panel_count"] for d in dashboards)
    return {"total_dashboards": len(dashboards), "total_panels": total_panels,
            "avg_panels": round(total_panels / max(len(dashboards), 1), 1)}

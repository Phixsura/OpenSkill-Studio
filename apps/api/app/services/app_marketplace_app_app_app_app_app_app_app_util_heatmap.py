"""Resource utilization heatmap — visualize utilization across time and services."""
from __future__ import annotations


def build_heatmap(services: list[str], time_slots: int, data: dict[str, list[float]]) -> dict:
    cells = []
    max_val = 0
    for svc in services:
        values = data.get(svc, [0] * time_slots)
        for i, val in enumerate(values[:time_slots]):
            cells.append({"service": svc, "slot": i, "value": round(val, 1)})
            if val > max_val:
                max_val = val
    hotspots = [c for c in cells if c["value"] > 80]
    avg_util = round(sum(c["value"] for c in cells) / max(len(cells), 1), 1)
    return {"cells": cells, "services": services, "time_slots": time_slots,
            "max_value": round(max_val, 1), "hotspot_count": len(hotspots),
            "avg_utilization": avg_util}

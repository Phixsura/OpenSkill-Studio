"""Custom metrics registry — define, record, and query custom business metrics."""
from __future__ import annotations
import time


class CustomMetricsRegistry:
    def __init__(self):
        self._metrics: dict[str, dict] = {}

    def define(self, name: str, *, metric_type: str = "counter",
               unit: str = "", description: str = "") -> dict:
        if metric_type not in ("counter", "gauge", "histogram"):
            return {"error": f"Invalid type: {metric_type}"}
        self._metrics[name] = {"name": name, "type": metric_type, "unit": unit,
                                "description": description, "values": [], "current": 0}
        return {"defined": name, "type": metric_type}

    def record(self, name: str, value: float, *, now: float | None = None) -> dict:
        m = self._metrics.get(name)
        if not m:
            return {"error": "Metric not defined"}
        ts = now if now is not None else time.time()
        m["values"].append({"value": value, "ts": ts})
        if m["type"] == "counter":
            m["current"] += value
        elif m["type"] == "gauge":
            m["current"] = value
        return {"name": name, "current": m["current"], "recorded": True}

    def query(self, name: str) -> dict:
        m = self._metrics.get(name)
        if not m:
            return {"error": "Metric not defined"}
        vals = [v["value"] for v in m["values"]]
        return {"name": name, "type": m["type"], "current": m["current"],
                "count": len(vals), "unit": m["unit"],
                "min": min(vals) if vals else 0, "max": max(vals) if vals else 0,
                "avg": round(sum(vals) / len(vals), 2) if vals else 0}

    def list_metrics(self) -> list[dict]:
        return [{"name": m["name"], "type": m["type"], "current": m["current"],
                 "unit": m["unit"], "data_points": len(m["values"])}
                for m in self._metrics.values()]

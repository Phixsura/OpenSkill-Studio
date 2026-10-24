"""Custom metrics registry — register and query custom application metrics."""
from __future__ import annotations
from collections import defaultdict


class CustomMetricsRegistry:
    def __init__(self):
        self._metrics: dict[str, dict] = {}
        self._data: dict[str, list[float]] = defaultdict(list)

    def register(self, name: str, unit: str, description: str = "") -> dict:
        self._metrics[name] = {"name": name, "unit": unit, "description": description}
        return self._metrics[name]

    def record(self, name: str, value: float) -> dict:
        self._data[name].append(value)
        return {"name": name, "recorded": True, "count": len(self._data[name])}

    def query(self, name: str) -> dict:
        values = self._data.get(name, [])
        if not values:
            return {"name": name, "count": 0}
        s = sorted(values)
        n = len(s)
        return {"name": name, "count": n, "min": s[0], "max": s[-1],
                "avg": round(sum(s) / n, 2), "sum": round(sum(s), 2),
                "unit": self._metrics.get(name, {}).get("unit", "")}

    def list_metrics(self) -> list[dict]:
        return [{"name": m["name"], "unit": m["unit"], "count": len(self._data.get(m["name"], []))}
                for m in sorted(self._metrics.values(), key=lambda m: m["name"])]

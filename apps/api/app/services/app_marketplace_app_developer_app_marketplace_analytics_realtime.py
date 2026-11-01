"""Realtime analytics — live metrics stream for marketplace dashboards."""

from datetime import datetime, timezone
from collections import deque


class RealtimeMetricsBuffer:
    def __init__(self, *, window_seconds: int = 60, max_points: int = 1000) -> None:
        self._buffer: deque = deque(maxlen=max_points)
        self._window = window_seconds

    def add(self, metric: str, value: float) -> None:
        self._buffer.append({"metric": metric, "value": value,
                              "timestamp": datetime.now(timezone.utc).isoformat()})

    def get_latest(self, metric: str, limit: int = 100) -> list[dict]:
        return [p for p in self._buffer if p["metric"] == metric][-limit:]

    def get_summary(self, metric: str) -> dict:
        points = [p["value"] for p in self._buffer if p["metric"] == metric]
        if not points:
            return {"metric": metric, "count": 0, "avg": 0, "min": 0, "max": 0}
        return {"metric": metric, "count": len(points),
                "avg": round(sum(points) / len(points), 2),
                "min": round(min(points), 2), "max": round(max(points), 2)}

    def get_all_metrics(self) -> list[str]:
        return list(set(p["metric"] for p in self._buffer))

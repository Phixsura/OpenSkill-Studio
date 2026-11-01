"""Real-time metrics streamer — stream live metrics to dashboards."""
from __future__ import annotations
import time


_streams: dict[str, list[dict]] = {}


def emit_metric(stream: str, name: str, value: float, tags: dict | None = None) -> dict:
    point = {"name": name, "value": value, "tags": tags or {},
             "timestamp": time.time()}
    _streams.setdefault(stream, []).append(point)
    return point


def get_stream(stream: str, last_n: int = 100) -> dict:
    points = _streams.get(stream, [])[-last_n:]
    if not points:
        return {"stream": stream, "points": [], "count": 0}
    values = [p["value"] for p in points]
    return {"stream": stream, "points": points, "count": len(points),
            "latest": points[-1]["value"],
            "avg": round(sum(values) / len(values), 2),
            "min": min(values), "max": max(values)}


def stream_stats() -> dict:
    return {"total_streams": len(_streams),
            "total_points": sum(len(pts) for pts in _streams.values()),
            "streams": list(_streams.keys())}


def clear_streams() -> None:
    _streams.clear()

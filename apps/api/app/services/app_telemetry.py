"""App telemetry — track usage patterns and performance metrics."""

from collections import defaultdict
from datetime import UTC, datetime

_telemetry: dict[str, list[dict]] = defaultdict(list)


def record_event(app_id: str, event: str, duration_ms: int = 0, metadata: dict | None = None) -> None:
    """Record a telemetry event."""
    _telemetry[app_id].append({
        "event": event,
        "duration_ms": duration_ms,
        "metadata": metadata or {},
        "timestamp": datetime.now(UTC).isoformat(),
    })


def get_performance_summary(app_id: str) -> dict:
    """Get performance summary: avg/p50/p95/p99 latencies."""
    events = _telemetry.get(app_id, [])
    durations = sorted([e["duration_ms"] for e in events if e["duration_ms"] > 0])
    if not durations:
        return {"count": 0, "avg_ms": 0, "p50_ms": 0, "p95_ms": 0, "p99_ms": 0}

    n = len(durations)
    return {
        "count": n,
        "avg_ms": round(sum(durations) / n, 1),
        "p50_ms": durations[n // 2],
        "p95_ms": durations[int(n * 0.95)],
        "p99_ms": durations[int(n * 0.99)],
    }


def clear_telemetry(app_id: str) -> int:
    count = len(_telemetry.pop(app_id, []))
    return count

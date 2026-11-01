"""Platform observability hub — unified observability across metrics, logs, traces."""
from __future__ import annotations
from collections import defaultdict
import time


class ObservabilityHub:
    def __init__(self):
        self._metrics: dict[str, list[float]] = defaultdict(list)
        self._logs: list[dict] = []
        self._traces: list[dict] = []
        self._alerts: list[dict] = []

    def record_metric(self, name: str, value: float, tags: dict | None = None) -> dict:
        self._metrics[name].append(value)
        return {"metric": name, "recorded": True, "count": len(self._metrics[name])}

    def record_log(self, level: str, message: str, source: str) -> dict:
        entry = {"level": level, "message": message, "source": source, "ts": time.time()}
        self._logs.append(entry)
        if level in ("error", "fatal"):
            self._alerts.append({"type": "log_alert", "source": source, "message": message})
        return {"logged": True, "total_logs": len(self._logs)}

    def record_trace(self, trace_id: str, spans: int, duration_ms: float) -> dict:
        self._traces.append({"trace_id": trace_id, "spans": spans, "duration_ms": duration_ms})
        return {"traced": True, "total_traces": len(self._traces)}

    def metric_summary(self, name: str) -> dict:
        values = self._metrics.get(name, [])
        if not values:
            return {"name": name, "count": 0}
        s = sorted(values)
        n = len(s)
        return {"name": name, "count": n, "min": s[0], "max": s[-1],
                "avg": round(sum(s) / n, 2), "p50": s[n // 2],
                "p95": s[int(n * 0.95)], "p99": s[int(n * 0.99)]}

    def dashboard(self) -> dict:
        log_levels = defaultdict(int)
        for log in self._logs:
            log_levels[log["level"]] += 1
        avg_trace_ms = round(sum(t["duration_ms"] for t in self._traces) / max(len(self._traces), 1), 1)
        return {"total_metrics": sum(len(v) for v in self._metrics.values()),
                "unique_metrics": len(self._metrics),
                "total_logs": len(self._logs),
                "log_levels": dict(log_levels),
                "total_traces": len(self._traces),
                "avg_trace_ms": avg_trace_ms,
                "active_alerts": len(self._alerts)}

    def recent_alerts(self, limit: int = 10) -> list[dict]:
        return self._alerts[-limit:]

    def clear_alerts(self) -> dict:
        count = len(self._alerts)
        self._alerts.clear()
        return {"cleared": count}

"""API traffic analyzer — analyze traffic patterns and detect anomalies."""
from __future__ import annotations
from collections import defaultdict
import math


def analyze_traffic(requests: list[dict]) -> dict:
    by_endpoint: dict[str, int] = defaultdict(int)
    by_method: dict[str, int] = defaultdict(int)
    by_status: dict[str, int] = defaultdict(int)
    total_latency = 0
    for r in requests:
        by_endpoint[r.get("endpoint", "/")] += 1
        by_method[r.get("method", "GET")] += 1
        status_bucket = f"{r.get('status', 200) // 100}xx"
        by_status[status_bucket] += 1
        total_latency += r.get("latency_ms", 0)
    avg_latency = round(total_latency / max(len(requests), 1), 1)
    error_rate = round(by_status.get("5xx", 0) / max(len(requests), 1) * 100, 2)
    top_endpoints = sorted(by_endpoint.items(), key=lambda x: -x[1])[:5]
    return {"total": len(requests), "by_method": dict(by_method),
            "by_status": dict(by_status), "avg_latency_ms": avg_latency,
            "error_rate_pct": error_rate,
            "top_endpoints": [{"endpoint": k, "count": v} for k, v in top_endpoints]}


def detect_traffic_spike(current_rps: float, baseline_rps: float, threshold_multiplier: float = 3.0) -> dict:
    ratio = round(current_rps / max(baseline_rps, 0.01), 2)
    spike = ratio > threshold_multiplier
    return {"current_rps": current_rps, "baseline_rps": baseline_rps,
            "ratio": ratio, "spike_detected": spike,
            "severity": "critical" if ratio > 10 else ("warning" if spike else "normal")}

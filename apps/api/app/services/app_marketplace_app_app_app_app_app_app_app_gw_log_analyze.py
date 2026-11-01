"""Gateway request log analyzer — analyze gateway logs for patterns."""
from __future__ import annotations
from collections import defaultdict


def analyze_gateway_logs(logs: list[dict]) -> dict:
    by_status: dict[str, int] = defaultdict(int)
    by_path: dict[str, int] = defaultdict(int)
    slow_requests = 0
    total_ms = 0
    for log in logs:
        bucket = f"{log.get('status', 200) // 100}xx"
        by_status[bucket] += 1
        by_path[log.get("path", "/")] += 1
        ms = log.get("duration_ms", 0)
        total_ms += ms
        if ms > 1000:
            slow_requests += 1
    avg_ms = round(total_ms / max(len(logs), 1), 1)
    top_paths = sorted(by_path.items(), key=lambda x: -x[1])[:5]
    return {"total": len(logs), "by_status": dict(by_status),
            "avg_duration_ms": avg_ms, "slow_requests": slow_requests,
            "top_paths": [{"path": k, "count": v} for k, v in top_paths]}

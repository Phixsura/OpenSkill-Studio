"""Request logger — HTTP request/response logging and analysis."""

import html
from collections import defaultdict
from datetime import datetime, timezone


def log_request(*, method: str, path: str, status_code: int,
                  duration_ms: int, user_agent: str = "") -> dict:
    return {"method": method.upper(), "path": html.escape(path),
            "status_code": status_code, "duration_ms": duration_ms,
            "user_agent": html.escape(user_agent[:100]),
            "success": 200 <= status_code < 400,
            "timestamp": datetime.now(timezone.utc).isoformat()}


def analyze_requests(*, logs: list[dict]) -> dict:
    total = len(logs)
    if not total:
        return {"total": 0, "avg_duration_ms": 0, "error_rate": 0, "top_paths": [], "status_dist": {}}
    durations = [l.get("duration_ms", 0) for l in logs]
    errors = sum(1 for l in logs if l.get("status_code", 0) >= 400)
    path_counts: dict[str, int] = defaultdict(int)
    status_dist: dict[int, int] = defaultdict(int)
    for l in logs:
        path_counts[l.get("path", "")] += 1
        status_dist[l.get("status_code", 0)] += 1
    top_paths = sorted(path_counts.items(), key=lambda x: -x[1])[:5]
    return {"total": total, "avg_duration_ms": round(sum(durations) / total),
            "p95_duration_ms": sorted(durations)[int(total * 0.95)] if total > 0 else 0,
            "error_rate": round(errors / total * 100, 1),
            "top_paths": [{"path": p, "count": c} for p, c in top_paths],
            "status_dist": dict(status_dist)}

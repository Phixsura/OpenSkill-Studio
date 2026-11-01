"""Request logger — structured HTTP request/response logging."""

import secrets
from datetime import datetime


def log_request(*, method: str, path: str, status_code: int, latency_ms: int,
                  user_id: str | None = None, ip: str | None = None,
                  user_agent: str | None = None) -> dict:
    level = "info" if status_code < 400 else "warn" if status_code < 500 else "error"
    return {
        "request_id": f"req_{secrets.token_urlsafe(10)}",
        "method": method.upper(),
        "path": path,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "user_id": user_id,
        "ip": ip,
        "user_agent": user_agent,
        "level": level,
        "timestamp": datetime.utcnow().isoformat(),
    }


def summarize_requests(*, logs: list[dict]) -> dict:
    total = len(logs)
    by_status: dict[int, int] = {}
    by_method: dict[str, int] = {}
    total_latency = 0
    errors = 0
    for log in logs:
        sc = log.get("status_code", 200)
        by_status[sc] = by_status.get(sc, 0) + 1
        m = log.get("method", "GET")
        by_method[m] = by_method.get(m, 0) + 1
        total_latency += log.get("latency_ms", 0)
        if sc >= 500:
            errors += 1
    return {
        "total_requests": total,
        "by_status": dict(sorted(by_status.items())),
        "by_method": by_method,
        "avg_latency_ms": round(total_latency / max(total, 1), 1),
        "error_count": errors,
        "error_rate": round(errors / max(total, 1) * 100, 2),
    }

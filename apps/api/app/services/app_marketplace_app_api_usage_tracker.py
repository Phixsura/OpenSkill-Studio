"""API usage tracker — track and report API endpoint usage patterns."""

from datetime import datetime


def track_api_call(*, endpoint: str, method: str, status_code: int,
                     latency_ms: int, api_key_prefix: str) -> dict:
    return {
        "endpoint": endpoint,
        "method": method.upper(),
        "status_code": status_code,
        "latency_ms": latency_ms,
        "api_key_prefix": api_key_prefix,
        "timestamp": datetime.utcnow().isoformat(),
        "success": 200 <= status_code < 400,
    }


def get_usage_report(*, calls: list[dict], period: str = "today") -> dict:
    total = len(calls)
    successful = sum(1 for c in calls if c.get("success"))
    avg_latency = round(sum(c.get("latency_ms", 0) for c in calls) / max(total, 1), 1)
    by_endpoint: dict[str, dict] = {}
    for c in calls:
        ep = f"{c.get('method', 'GET')} {c.get('endpoint', '/')}"
        if ep not in by_endpoint:
            by_endpoint[ep] = {"count": 0, "total_latency": 0, "errors": 0}
        by_endpoint[ep]["count"] += 1
        by_endpoint[ep]["total_latency"] += c.get("latency_ms", 0)
        if not c.get("success"):
            by_endpoint[ep]["errors"] += 1
    endpoints = []
    for ep, data in sorted(by_endpoint.items(), key=lambda x: x[1]["count"], reverse=True):
        endpoints.append({
            "endpoint": ep, "count": data["count"],
            "avg_latency_ms": round(data["total_latency"] / data["count"], 1),
            "error_count": data["errors"],
        })
    return {
        "period": period,
        "total_calls": total,
        "success_rate": round(successful / max(total, 1) * 100, 1),
        "avg_latency_ms": avg_latency,
        "endpoints": endpoints[:10],
    }

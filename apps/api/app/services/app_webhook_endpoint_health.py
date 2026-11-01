"""Webhook endpoint health — track per-endpoint delivery health."""

from collections import defaultdict


_endpoint_stats: dict[str, dict] = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0, "avg_ms": 0, "total_ms": 0})


def record_delivery(endpoint: str, *, success: bool, duration_ms: int) -> None:
    s = _endpoint_stats[endpoint]
    s["total"] += 1
    s["total_ms"] += duration_ms
    s["avg_ms"] = round(s["total_ms"] / s["total"], 1)
    if success:
        s["success"] += 1
    else:
        s["failure"] += 1


def get_endpoint_health(endpoint: str) -> dict:
    s = _endpoint_stats.get(endpoint)
    if not s or s["total"] == 0:
        return {"status": "unknown", "success_rate": 0, "avg_ms": 0, "total": 0}
    rate = round(s["success"] / s["total"] * 100, 1)
    status = "healthy" if rate >= 95 else "degraded" if rate >= 80 else "unhealthy"
    return {"status": status, "success_rate": rate, "avg_ms": s["avg_ms"], "total": s["total"]}


def list_unhealthy_endpoints() -> list[dict]:
    return [{"endpoint": ep, **get_endpoint_health(ep)} for ep in _endpoint_stats
            if get_endpoint_health(ep)["status"] != "healthy"]

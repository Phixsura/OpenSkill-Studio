"""Endpoint health matrix — monitor health of all API endpoints."""
from __future__ import annotations


def build_health_matrix(endpoints: list[dict]) -> dict:
    matrix = []
    healthy = 0
    for ep in endpoints:
        status = "healthy" if ep.get("p99_ms", 0) < ep.get("slo_ms", 500) and ep.get("error_rate", 0) < 1 else "degraded" if ep.get("error_rate", 0) < 5 else "unhealthy"
        if status == "healthy":
            healthy += 1
        matrix.append({"path": ep["path"], "method": ep.get("method", "GET"),
                       "p99_ms": ep.get("p99_ms", 0), "error_rate": ep.get("error_rate", 0),
                       "rpm": ep.get("rpm", 0), "status": status})
    total = len(matrix)
    return {"matrix": matrix, "total": total, "healthy": healthy,
            "degraded": sum(1 for m in matrix if m["status"] == "degraded"),
            "unhealthy": sum(1 for m in matrix if m["status"] == "unhealthy"),
            "health_pct": round(healthy / max(total, 1) * 100)}

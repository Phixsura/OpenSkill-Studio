"""Service health matrix — comprehensive health view across all services."""
from __future__ import annotations


def build_health_matrix(services: list[dict]) -> dict:
    matrix = []
    healthy = 0
    for s in services:
        dims = {"uptime": s.get("uptime_pct", 100) >= 99.9,
                "latency": s.get("p99_ms", 0) < 500,
                "errors": s.get("error_rate", 0) < 1,
                "saturation": s.get("cpu_pct", 0) < 80}
        score = sum(dims.values())
        status = "healthy" if score == 4 else "degraded" if score >= 2 else "unhealthy"
        if status == "healthy":
            healthy += 1
        matrix.append({"service": s["name"], "status": status, "score": score, "dimensions": dims})
    return {"matrix": matrix, "total": len(matrix), "healthy": healthy,
            "health_pct": round(healthy / max(len(matrix), 1) * 100)}


def identify_weakest(matrix: dict) -> dict:
    if not matrix["matrix"]:
        return {"weakest": None}
    weakest = min(matrix["matrix"], key=lambda s: s["score"])
    failed_dims = [d for d, ok in weakest["dimensions"].items() if not ok]
    return {"weakest": weakest["service"], "score": weakest["score"],
            "failed_dimensions": failed_dims}

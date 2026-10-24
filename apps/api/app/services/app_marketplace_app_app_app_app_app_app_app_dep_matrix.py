"""Service dependency health matrix — cross-service health matrix."""
from __future__ import annotations


def build_matrix(services: list[str], checks: list[dict]) -> dict:
    matrix: dict[str, dict[str, str]] = {s: {} for s in services}
    for check in checks:
        src = check["source"]
        dst = check["destination"]
        status = check.get("status", "unknown")
        if src in matrix:
            matrix[src][dst] = status
    healthy_pairs = sum(1 for row in matrix.values() for s in row.values() if s == "healthy")
    total_pairs = sum(len(row) for row in matrix.values())
    return {"matrix": matrix, "services": services,
            "healthy_pairs": healthy_pairs, "total_pairs": total_pairs,
            "health_pct": round(healthy_pairs / max(total_pairs, 1) * 100, 1)}

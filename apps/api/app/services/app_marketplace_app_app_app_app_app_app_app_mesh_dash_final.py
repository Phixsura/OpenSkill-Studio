"""Service mesh dashboard final — the complete mesh observability view."""
from __future__ import annotations


def mesh_dashboard_final(mesh: dict) -> dict:
    services = mesh.get("services", [])
    healthy = sum(1 for s in services if s.get("healthy"))
    total = len(services)
    rps = mesh.get("total_rps", 0)
    error_rate = mesh.get("error_rate_pct", 0)
    p99 = mesh.get("p99_ms", 0)
    mtls = sum(1 for s in services if s.get("mtls"))
    mtls_pct = round(mtls / max(total, 1) * 100, 1)
    circuit_trips = mesh.get("circuit_trips", 0)
    retries = mesh.get("total_retries", 0)
    score = 100
    if healthy < total: score -= (total - healthy) * 5
    if error_rate > 1: score -= 10
    if p99 > 500: score -= 10
    if circuit_trips > 0: score -= min(circuit_trips * 5, 20)
    score = max(0, score)
    status = "healthy" if score >= 80 else ("degraded" if score >= 50 else "critical")
    return {"score": score, "status": status, "healthy": healthy, "total": total,
            "rps": rps, "error_rate_pct": error_rate, "p99_ms": p99,
            "mtls_pct": mtls_pct, "circuit_trips": circuit_trips, "retries": retries}

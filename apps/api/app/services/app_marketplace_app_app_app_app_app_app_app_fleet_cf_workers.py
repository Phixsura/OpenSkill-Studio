"""Fleet Cloudflare Workers — track edge computing health."""
from __future__ import annotations
def fleet_cf_workers_status(workers: list[dict]) -> dict:
    active = [w for w in workers if w.get("active", True)]
    total_requests = sum(w.get("requests_24h", 0) for w in workers)
    errors = sum(w.get("errors_24h", 0) for w in workers)
    cpu_time_ms = sum(w.get("avg_cpu_ms", 0) for w in workers) / max(len(workers), 1)
    return {"workers": len(workers), "active": len(active), "requests_24h": total_requests,
            "errors_24h": errors, "avg_cpu_ms": round(cpu_time_ms, 1), "healthy": errors == 0}

"""Service readiness probe — check if services are ready to receive traffic."""
from __future__ import annotations


def probe_readiness(services: list[dict]) -> dict:
    results = []
    ready = 0
    for s in services:
        checks = s.get("checks", {})
        db_ok = checks.get("database", False)
        cache_ok = checks.get("cache", True)
        config_ok = checks.get("config_loaded", False)
        all_ok = db_ok and cache_ok and config_ok
        if all_ok:
            ready += 1
        results.append({"service": s["name"], "ready": all_ok,
                         "checks": {"database": db_ok, "cache": cache_ok, "config": config_ok}})
    return {"services": results, "total": len(results), "ready": ready,
            "not_ready": len(results) - ready, "all_ready": ready == len(results)}


def readiness_report(probes: list[dict]) -> dict:
    all_ready = all(p.get("all_ready", False) for p in probes)
    total_services = sum(p.get("total", 0) for p in probes)
    total_ready = sum(p.get("ready", 0) for p in probes)
    return {"total_probes": len(probes), "total_services": total_services,
            "total_ready": total_ready, "all_ready": all_ready,
            "readiness_pct": round(total_ready / max(total_services, 1) * 100)}

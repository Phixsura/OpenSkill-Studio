"""Service dependency checker — verify all deps are healthy."""
from __future__ import annotations


def check_dependencies(deps: list[dict]) -> dict:
    results = []
    all_ok = True
    for d in deps:
        healthy = d.get("status") == "healthy"
        latency = d.get("latency_ms", 0)
        timeout = latency > d.get("timeout_ms", 5000)
        ok = healthy and not timeout
        if not ok:
            all_ok = False
        results.append({"name": d["name"], "type": d.get("type", "service"),
                        "healthy": ok, "latency_ms": latency, "timeout": timeout})
    critical = [r for r in results if not r["healthy"]]
    return {"dependencies": results, "total": len(results),
            "healthy": sum(1 for r in results if r["healthy"]),
            "unhealthy": len(critical), "all_ok": all_ok,
            "critical_failures": [c["name"] for c in critical]}


def suggest_fallbacks(failures: list[str], fallback_map: dict[str, str]) -> list[dict]:
    return [{"service": f, "fallback": fallback_map.get(f, "none"),
             "has_fallback": f in fallback_map} for f in failures]

"""Health monitor v2 — advanced multi-probe health checking."""

from datetime import datetime, timezone


def run_health_probes(*, probes: list[dict]) -> dict:
    results = []
    for probe in probes:
        # Simulate probe execution
        result = {"name": probe["name"], "type": probe.get("type", "http"),
                  "status": "pass" if probe.get("mock_healthy", True) else "fail",
                  "latency_ms": probe.get("mock_latency", 50),
                  "checked_at": datetime.now(timezone.utc).isoformat()}
        results.append(result)
    passed = sum(1 for r in results if r["status"] == "pass")
    return {"probes": results, "passed": passed, "total": len(results),
            "overall": "healthy" if passed == len(results) else "degraded" if passed > 0 else "down"}


def compute_availability_sli(*, results_history: list[dict], window_hours: int = 24) -> dict:
    if not results_history:
        return {"sli_pct": 100.0, "checks": 0, "window_hours": window_hours}
    healthy = sum(1 for r in results_history if r.get("overall") == "healthy")
    return {"sli_pct": round(healthy / len(results_history) * 100, 3),
            "checks": len(results_history), "window_hours": window_hours}


def build_health_timeline(*, checks: list[dict]) -> list[dict]:
    return [{"time": c.get("checked_at", ""), "status": c.get("overall", "unknown"),
             "passed": c.get("passed", 0), "total": c.get("total", 0)} for c in checks[-48:]]

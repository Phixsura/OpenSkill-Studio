"""Fleet New Relic — track New Relic APM integration."""
from __future__ import annotations
def fleet_newrelic_status(apps: list[dict]) -> dict:
    reporting = [a for a in apps if a.get("reporting", True)]
    apdex_avg = round(sum(a.get("apdex", 0) for a in reporting) / max(len(reporting), 1), 3)
    error_rate = round(sum(a.get("error_rate_pct", 0) for a in reporting) / max(len(reporting), 1), 2)
    return {"total": len(apps), "reporting": len(reporting), "apdex_avg": apdex_avg,
            "error_rate": error_rate, "healthy": apdex_avg >= 0.9}

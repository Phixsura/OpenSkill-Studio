"""Incident auto-resolver — auto-resolve incidents based on recovery signals."""
from __future__ import annotations


def should_auto_resolve(incident: dict, recovery_signals: dict) -> dict:
    checks = {
        "error_rate_normal": recovery_signals.get("error_rate_pct", 100) < 1,
        "latency_normal": recovery_signals.get("p99_ms", 9999) < recovery_signals.get("baseline_p99_ms", 500) * 1.2,
        "uptime_restored": recovery_signals.get("uptime_pct", 0) >= 99.9,
        "no_alerts": recovery_signals.get("active_alerts", 1) == 0,
    }
    all_clear = all(checks.values())
    passed = sum(1 for v in checks.values() if v)
    return {"auto_resolve": all_clear, "checks": checks,
            "passed": passed, "total": len(checks),
            "incident_id": incident.get("id", ""),
            "recommendation": "resolve" if all_clear else "keep_open"}


def resolution_summary(incidents: list[dict]) -> dict:
    auto_resolved = sum(1 for i in incidents if i.get("auto_resolved"))
    manual = sum(1 for i in incidents if not i.get("auto_resolved") and i.get("resolved"))
    open_count = sum(1 for i in incidents if not i.get("resolved"))
    return {"total": len(incidents), "auto_resolved": auto_resolved,
            "manual_resolved": manual, "open": open_count}

"""Fleet Sentry — track error monitoring and crash reporting."""
from __future__ import annotations
def fleet_sentry_status(projects: list[dict]) -> dict:
    total_events = sum(p.get("events_24h", 0) for p in projects)
    unresolved = sum(p.get("unresolved_issues", 0) for p in projects)
    crash_free = round(sum(p.get("crash_free_pct", 100) for p in projects) / max(len(projects), 1), 1)
    return {"projects": len(projects), "events_24h": total_events,
            "unresolved": unresolved, "crash_free_pct": crash_free, "healthy": crash_free >= 99}

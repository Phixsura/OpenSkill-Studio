"""Fleet Error Tracking v9 — track application error rates and grouping."""
from __future__ import annotations
def fleet_error_tracking_v9(apps: list[dict]) -> dict:
    total_errors = sum(a.get("errors_today", 0) for a in apps)
    unique_errors = sum(a.get("unique_errors", 0) for a in apps)
    resolved = sum(a.get("resolved", 0) for a in apps)
    return {"apps": len(apps), "errors_today": total_errors, "unique_errors": unique_errors,
            "resolved": resolved, "healthy": total_errors < 100}

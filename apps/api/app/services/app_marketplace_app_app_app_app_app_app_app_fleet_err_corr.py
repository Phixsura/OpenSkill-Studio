"""Fleet error correlation — find correlated error patterns."""
from __future__ import annotations
def fleet_error_correlation(errors: list[dict]) -> dict:
    by_svc: dict[str, int] = {}
    for e in errors:
        svc = e.get("service", "unknown")
        by_svc[svc] = by_svc.get(svc, 0) + 1
    hotspot = max(by_svc, key=lambda k: by_svc[k]) if by_svc else None
    return {"total_errors": len(errors), "services_affected": len(by_svc),
            "hotspot": hotspot, "cascading": len(by_svc) > 3}

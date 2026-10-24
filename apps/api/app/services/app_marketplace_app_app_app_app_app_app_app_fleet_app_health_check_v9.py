"""Fleet App Health Check v9 — track application-level health probes."""
from __future__ import annotations
def fleet_app_health_check_v9(checks: list[dict]) -> dict:
    liveness = [c for c in checks if c.get("type") == "liveness" and c.get("passing")]
    readiness = [c for c in checks if c.get("type") == "readiness" and c.get("passing")]
    startup = [c for c in checks if c.get("type") == "startup" and c.get("passing")]
    return {"checks": len(checks), "liveness_ok": len(liveness), "readiness_ok": len(readiness),
            "startup_ok": len(startup), "healthy": True}

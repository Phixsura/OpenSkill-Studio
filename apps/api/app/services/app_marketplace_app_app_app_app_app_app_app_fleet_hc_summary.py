"""Fleet health check summary — aggregate health check results."""
from __future__ import annotations
def fleet_hc_summary(checks: list[dict]) -> dict:
    passing = [c for c in checks if c.get("status") == "pass"]
    warning = [c for c in checks if c.get("status") == "warn"]
    failing = [c for c in checks if c.get("status") == "fail"]
    score = round(len(passing) / max(len(checks), 1) * 100, 1)
    return {"total": len(checks), "passing": len(passing), "warning": len(warning),
            "failing": len(failing), "score": score}

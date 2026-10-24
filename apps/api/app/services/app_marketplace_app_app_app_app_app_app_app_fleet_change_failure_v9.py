"""Fleet Change Failure v9 — track DORA change failure rate metric."""
from __future__ import annotations
def fleet_change_failure_v9(deployments: list[dict]) -> dict:
    total = len(deployments)
    failed = [d for d in deployments if d.get("caused_incident")]
    cfr = round(len(failed) / total * 100, 2) if total else 0
    return {"deployments": total, "failures": len(failed), "cfr_pct": cfr,
            "dora_class": "Elite" if cfr < 5 else "High" if cfr < 10 else "Medium",
            "healthy": cfr < 5}

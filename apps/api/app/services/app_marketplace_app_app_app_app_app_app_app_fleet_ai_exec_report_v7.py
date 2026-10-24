"""Fleet AI Executive Report v7 — track C-suite AI platform reporting."""
from __future__ import annotations
def fleet_ai_exec_report_v7(reporters: list[dict]) -> dict:
    active = [r for r in reporters if r.get("active", True)]
    reports_30d = sum(r.get("reports", 0) for r in reporters)
    stakeholders = sum(r.get("stakeholders", 0) for r in reporters)
    kpis = sum(r.get("kpis", 0) for r in reporters)
    return {"reporters": len(reporters), "active": len(active), "reports": reports_30d,
            "stakeholders": stakeholders, "kpis": kpis, "reporting": reports_30d > 0}

"""Fleet GDPR compliance — track GDPR readiness."""
from __future__ import annotations
def fleet_gdpr_compliance(controls: list[dict]) -> dict:
    met = [c for c in controls if c.get("met", False)]
    score = round(len(met) / max(len(controls), 1) * 100, 1)
    return {"total": len(controls), "met": len(met), "unmet": len(controls) - len(met),
            "score": score, "compliant": score == 100}

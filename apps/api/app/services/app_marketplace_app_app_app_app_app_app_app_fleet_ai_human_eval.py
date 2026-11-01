"""Fleet AI Human Eval — track human evaluation of AI outputs."""
from __future__ import annotations
def fleet_ai_human_eval(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    evaluations_24h = sum(s.get("evals_24h", 0) for s in systems)
    evaluators = sum(s.get("evaluators", 0) for s in systems)
    agreement_pct = round(sum(s.get("agreement_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "evals_24h": evaluations_24h,
            "evaluators": evaluators, "agreement_pct": agreement_pct, "calibrated": agreement_pct > 80}

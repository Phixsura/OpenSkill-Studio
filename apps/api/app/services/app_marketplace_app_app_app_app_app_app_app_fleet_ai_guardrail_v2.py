"""Fleet AI Guardrail Engine v2 — track advanced AI safety guardrails."""
from __future__ import annotations
def fleet_ai_guardrail_v2(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    evaluations_24h = sum(e.get("evals_24h", 0) for e in engines)
    blocked = sum(e.get("blocked", 0) for e in engines)
    rules = sum(e.get("rules", 0) for e in engines)
    return {"engines": len(engines), "active": len(active), "evals_24h": evaluations_24h,
            "blocked": blocked, "rules": rules, "protecting": rules > 0}

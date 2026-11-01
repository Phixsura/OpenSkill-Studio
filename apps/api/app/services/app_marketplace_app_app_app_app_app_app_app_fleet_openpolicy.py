"""Fleet OpenPolicy — track policy-as-code adoption."""
from __future__ import annotations
def fleet_openpolicy(repos: list[dict]) -> dict:
    with_policy = [r for r in repos if r.get("has_policy_tests", False)]
    automated = [r for r in repos if r.get("policy_ci_enforced", False)]
    pct = round(len(with_policy) / max(len(repos), 1) * 100, 1)
    return {"total": len(repos), "with_policy": len(with_policy), "ci_enforced": len(automated),
            "coverage_pct": pct, "mature": pct >= 80}

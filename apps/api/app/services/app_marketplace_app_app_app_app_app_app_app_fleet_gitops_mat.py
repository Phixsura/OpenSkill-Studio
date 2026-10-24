"""Fleet GitOps maturity — assess GitOps adoption level."""
from __future__ import annotations
def fleet_gitops_maturity(dimensions: dict) -> dict:
    declarative = dimensions.get("declarative_pct", 0)
    automated = dimensions.get("automated_sync_pct", 0)
    immutable = dimensions.get("immutable_infra_pct", 0)
    score = round((declarative + automated + immutable) / 3, 1)
    level = "Level 4" if score >= 90 else ("Level 3" if score >= 70 else ("Level 2" if score >= 50 else "Level 1"))
    return {"score": score, "level": level, "declarative": declarative,
            "automated": automated, "immutable": immutable}

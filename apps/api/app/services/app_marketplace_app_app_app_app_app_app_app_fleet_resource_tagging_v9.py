"""Fleet Resource Tagging v9 — track cloud resource tagging compliance."""
from __future__ import annotations
def fleet_resource_tagging_v9(resources: list[dict]) -> dict:
    tagged = [r for r in resources if r.get("tags")]
    untagged = [r for r in resources if not r.get("tags")]
    required_tags = ["env", "team", "cost-center"]
    compliant = [r for r in resources if all(t in (r.get("tags") or {}) for t in required_tags)]
    return {"total": len(resources), "tagged": len(tagged), "untagged": len(untagged),
            "compliant": len(compliant), "healthy": len(untagged) == 0}
